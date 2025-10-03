# HMS Ultra Nginx and SSL Configuration

This document explains the nginx configuration and SSL certificate setup for the HMS Ultra application.

## Overview

The HMS Ultra application uses nginx as a reverse proxy to serve the Django application with SSL/TLS encryption for secure communication.

## File Structure

```
hms/
├── config/
│   ├── nginx/
│   │   └── nginx.conf          # Nginx configuration file
│   └── ssl/
│       ├── hms_ultra.crt       # SSL certificate
│       └── hms_ultra.key       # SSL private key
├── config/deployment/
│   ├── docker-compose.yml      # Development configuration
│   └── docker-compose.prod.yml # Production configuration
└── scripts/deployment/
    └── generate-ssl-certs.sh   # SSL certificate generation script
```

## Nginx Configuration

### Location
- **File**: `config/nginx/nginx.conf`
- **Container Mount**: `/etc/nginx/nginx.conf`

### Features
- Reverse proxy to Django application
- Static file serving
- SSL/TLS termination
- Rate limiting
- Health check endpoint

## SSL Certificates

### Development Certificates
- **Location**: `config/ssl/`
- **Type**: Self-signed certificates
- **Validity**: 365 days
- **Purpose**: Local development and testing

### Certificate Files
- `hms_ultra.crt` - SSL certificate
- `hms_ultra.key` - Private key

### Generation
```bash
# Generate development SSL certificates
cd scripts/deployment/
./generate-ssl-certs.sh

# Or generate manually
openssl req -x509 -newkey rsa:4096 \
  -keyout config/ssl/hms_ultra.key \
  -out config/ssl/hms_ultra.crt \
  -days 365 -nodes \
  -subj "/C=US/ST=State/L=City/O=HMS Ultra/OU=IT Department/CN=localhost"
```

## Docker Compose Configuration

### Development (docker-compose.yml)
```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ../nginx/nginx.conf:/etc/nginx/nginx.conf
    - static_volume:/var/www/hms_ultra/static
    - media_volume:/var/www/hms_ultra/media
    - ../ssl:/etc/nginx/ssl
  depends_on:
    - web
```

### Production (docker-compose.prod.yml)
```yaml
nginx:
  image: nginx:alpine
  volumes:
    - ../nginx/nginx.conf:/etc/nginx/nginx.conf
    - static_volume:/app/staticfiles
    - media_volume:/app/media
    - ../ssl:/etc/nginx/ssl
  ports:
    - "80:80"
    - "443:443"
  depends_on:
    - web
  restart: unless-stopped
```

## Volume Mounts Explained

### Nginx Configuration
- **Host Path**: `../nginx/nginx.conf`
- **Container Path**: `/etc/nginx/nginx.conf`
- **Purpose**: Main nginx configuration file

### SSL Certificates
- **Host Path**: `../ssl`
- **Container Path**: `/etc/nginx/ssl`
- **Purpose**: SSL certificates and private keys

### Static Files
- **Development**: `static_volume:/var/www/hms_ultra/static`
- **Production**: `static_volume:/app/staticfiles`
- **Purpose**: Django static files (CSS, JS, images)

### Media Files
- **Development**: `media_volume:/var/www/hms_ultra/media`
- **Production**: `media_volume:/app/media`
- **Purpose**: User-uploaded files

## Path Resolution

Since the docker-compose files are located in `config/deployment/`, the relative paths are:

- `../nginx/nginx.conf` → `config/nginx/nginx.conf`
- `../ssl` → `config/ssl`

## SSL Configuration in Nginx

### Basic SSL Setup
```nginx
server {
    listen 443 ssl http2;
    server_name localhost;
    
    ssl_certificate     /etc/nginx/ssl/hms_ultra.crt;
    ssl_certificate_key /etc/nginx/ssl/hms_ultra.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
}
```

## Development vs Production

### Development
- Uses self-signed certificates
- HTTP and HTTPS both available
- Debug mode enabled
- Local domain (localhost)

### Production
- Should use trusted CA certificates
- HTTPS only (HTTP redirects to HTTPS)
- Security headers enabled
- Production domain

## Troubleshooting

### Common Issues

#### 1. Certificate Not Found
```bash
# Error: SSL certificate file not found
# Solution: Check if certificates exist
ls -la config/ssl/
```

#### 2. Permission Denied
```bash
# Error: Permission denied on SSL files
# Solution: Check file permissions
chmod 644 config/ssl/hms_ultra.crt
chmod 600 config/ssl/hms_ultra.key
```

#### 3. Nginx Config Not Found
```bash
# Error: nginx.conf not found
# Solution: Check if nginx config exists
ls -la config/nginx/nginx.conf
```

#### 4. Volume Mount Issues
```bash
# Error: Volume mount failed
# Solution: Verify relative paths from docker-compose location
cd config/deployment/
ls -la ../nginx/nginx.conf
ls -la ../ssl/
```

### Verification Commands

#### Check SSL Certificates
```bash
# Verify certificate
openssl x509 -in config/ssl/hms_ultra.crt -text -noout

# Check certificate validity
openssl x509 -in config/ssl/hms_ultra.crt -dates -noout
```

#### Test Nginx Configuration
```bash
# Test nginx config syntax
docker run --rm -v $(pwd)/config/nginx/nginx.conf:/etc/nginx/nginx.conf nginx:alpine nginx -t
```

#### Check Container Mounts
```bash
# Inspect nginx container mounts
docker-compose -f config/deployment/docker-compose.yml exec nginx ls -la /etc/nginx/
```

## Security Considerations

### Development
- Self-signed certificates are acceptable
- Browser warnings are expected
- Use for local development only

### Production
- Use certificates from trusted CA
- Implement proper SSL/TLS configuration
- Enable security headers
- Regular certificate renewal

### Best Practices
1. **Certificate Management**: Use automated renewal
2. **Security Headers**: Implement HSTS, CSP, etc.
3. **TLS Configuration**: Use strong ciphers and protocols
4. **Monitoring**: Monitor certificate expiration
5. **Backup**: Secure backup of private keys

## Production SSL Setup

### Let's Encrypt (Recommended)
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --webroot -w /var/www/html -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Commercial CA
1. Generate Certificate Signing Request (CSR)
2. Submit to Certificate Authority
3. Install issued certificate
4. Configure nginx to use new certificate

## Monitoring

### Certificate Expiration
```bash
# Check certificate expiration
openssl x509 -in config/ssl/hms_ultra.crt -dates -noout

# Monitor with script
#!/bin/bash
EXPIRY=$(openssl x509 -in config/ssl/hms_ultra.crt -enddate -noout | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
CURRENT_EPOCH=$(date +%s)
DAYS_LEFT=$(( (EXPIRY_EPOCH - CURRENT_EPOCH) / 86400 ))
echo "Certificate expires in $DAYS_LEFT days"
```

## Support

For issues with nginx or SSL configuration:
1. Check this documentation
2. Verify file paths and permissions
3. Test nginx configuration syntax
4. Review Docker container logs
5. Check certificate validity

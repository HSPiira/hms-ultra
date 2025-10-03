# HMS Ultra Nginx Configuration Guide

This document explains the nginx configuration structure and setup for the HMS Ultra application.

## Overview

The HMS Ultra nginx configuration is a standalone configuration file that provides:
- Reverse proxy to Django application
- Static file serving
- SSL/TLS termination
- Rate limiting
- Security headers
- Performance optimizations

## Configuration Structure

### File Location
- **Path**: `config/nginx/nginx.conf`
- **Type**: Standalone nginx configuration
- **Purpose**: Complete nginx configuration for HMS Ultra

### Required Blocks

#### 1. Events Block
```nginx
events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}
```

**Purpose**: Defines how nginx handles connections
- `worker_connections`: Maximum connections per worker process
- `use epoll`: Efficient event processing method
- `multi_accept`: Accept multiple connections at once

#### 2. HTTP Block
```nginx
http {
    # Basic configuration
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging configuration
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    # Performance settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 20M;
}
```

**Purpose**: Main HTTP configuration
- **MIME Types**: Proper content type handling
- **Logging**: Access and error logging
- **Performance**: Optimized file transfer and connection handling
- **Security**: File upload size limits

#### 3. Rate Limiting
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
```

**Purpose**: API rate limiting
- **Zone**: `api` with 10MB memory
- **Rate**: 10 requests per second per IP
- **Scope**: Applied to `/api/` endpoints

#### 4. Upstream Configuration
```nginx
upstream web {
    server web:8000;
}
```

**Purpose**: Defines backend server
- **Server**: Django application container
- **Port**: 8000 (Django development server)
- **Load Balancing**: Single server (can be extended)

#### 5. Server Block
```nginx
server {
    listen 80;
    server_name _;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

**Purpose**: HTTP server configuration
- **Port**: 80 (HTTP)
- **Security**: Multiple security headers
- **Headers**: XSS protection, content type sniffing prevention

## Location Blocks

### 1. Static Files
```nginx
location /static/ {
    alias /app/staticfiles/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

**Purpose**: Serve Django static files
- **Path**: `/static/` → `/app/staticfiles/`
- **Caching**: 1 year expiration
- **Headers**: Public, immutable cache control

### 2. Media Files
```nginx
location /media/ {
    alias /app/media/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

**Purpose**: Serve user-uploaded files
- **Path**: `/media/` → `/app/media/`
- **Caching**: 1 year expiration
- **Headers**: Public, immutable cache control

### 3. Health Check
```nginx
location /health/ {
    proxy_pass http://web;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Purpose**: Health check endpoint
- **Proxy**: Direct to Django application
- **Headers**: Preserve client information
- **Monitoring**: Container health checks

### 4. API Endpoints
```nginx
location /api/ {
    proxy_pass http://web;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Rate limiting
    limit_req zone=api burst=20 nodelay;
}
```

**Purpose**: API request handling
- **Proxy**: Forward to Django application
- **Rate Limiting**: 10 req/s with 20 burst
- **Headers**: Preserve client information

### 5. Admin Interface
```nginx
location /admin/ {
    proxy_pass http://web;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Purpose**: Django admin interface
- **Proxy**: Forward to Django application
- **Headers**: Preserve client information
- **Access**: Django admin authentication

### 6. Default Location
```nginx
location / {
    proxy_pass http://web;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Purpose**: Catch-all for other requests
- **Proxy**: Forward to Django application
- **Headers**: Preserve client information
- **Fallback**: Handle all other requests

## Performance Optimizations

### Gzip Compression
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_proxied any;
gzip_comp_level 6;
gzip_types
    text/plain
    text/css
    text/xml
    text/javascript
    application/json
    application/javascript
    application/xml+rss
    application/atom+xml
    image/svg+xml;
```

**Benefits**:
- **Compression**: Reduces bandwidth usage
- **Types**: Compresses text-based files
- **Level**: Balanced compression ratio
- **Min Length**: Only compress files > 1KB

### Connection Handling
```nginx
sendfile on;
tcp_nopush on;
tcp_nodelay on;
keepalive_timeout 65;
```

**Benefits**:
- **Sendfile**: Efficient file transfer
- **TCP Optimizations**: Better network performance
- **Keepalive**: Reuse connections

## Security Features

### Security Headers
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

**Protection**:
- **X-Frame-Options**: Prevents clickjacking
- **X-Content-Type-Options**: Prevents MIME sniffing
- **X-XSS-Protection**: Browser XSS protection
- **Referrer-Policy**: Controls referrer information

### Rate Limiting
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;
```

**Protection**:
- **Zone**: 10MB memory for rate limiting
- **Rate**: 10 requests per second
- **Burst**: Allow 20 requests in burst
- **Nodelay**: Don't delay burst requests

## Validation

### Configuration Validation
```bash
# Test nginx configuration
./scripts/deployment/validate-nginx-config.sh
```

**Checks**:
- ✅ Events block present
- ✅ HTTP block present
- ✅ Server block present
- ✅ Upstream configuration
- ✅ Proxy configuration

### Docker Validation
```bash
# Test with Docker
docker run --rm -v $(pwd)/config/nginx/nginx.conf:/etc/nginx/nginx.conf nginx:alpine nginx -t
```

## Troubleshooting

### Common Issues

#### 1. Missing Events Block
```bash
# Error: nginx: [emerg] "events" directive is not allowed here
# Solution: Add events block before http block
```

#### 2. Configuration Syntax Error
```bash
# Error: nginx: [emerg] unexpected "}" in /etc/nginx/nginx.conf
# Solution: Check for missing or extra braces
```

#### 3. Upstream Server Unavailable
```bash
# Error: connect() failed (111: Connection refused)
# Solution: Ensure Django application is running on port 8000
```

### Debugging Commands

#### Check Configuration
```bash
# Validate syntax
nginx -t

# Check configuration
nginx -T
```

#### Monitor Logs
```bash
# Access logs
tail -f /var/log/nginx/access.log

# Error logs
tail -f /var/log/nginx/error.log
```

#### Test Endpoints
```bash
# Health check
curl http://localhost/health/

# API endpoint
curl http://localhost/api/health/

# Static files
curl http://localhost/static/admin/css/base.css
```

## Production Considerations

### SSL/TLS Configuration
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/hms_ultra.crt;
    ssl_certificate_key /etc/nginx/ssl/hms_ultra.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
}
```

### Load Balancing
```nginx
upstream web {
    server web1:8000;
    server web2:8000;
    server web3:8000;
}
```

### Caching
```nginx
location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 1h;
    proxy_cache_key $scheme$proxy_host$request_uri;
}
```

## Monitoring

### Health Checks
```bash
# Container health
docker-compose ps

# Nginx status
curl -f http://localhost/health/

# Application health
curl -f http://localhost/api/health/
```

### Performance Monitoring
```bash
# Connection statistics
ss -tuln | grep :80

# Process monitoring
ps aux | grep nginx

# Memory usage
free -h
```

## Support

For nginx configuration issues:
1. Check this documentation
2. Validate configuration syntax
3. Review error logs
4. Test with minimal configuration
5. Verify upstream server availability

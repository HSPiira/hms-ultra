# SSL Certificates for HMS Ultra

This directory contains SSL certificates for the HMS Ultra application.

## Files

- `hms_ultra.crt` - SSL certificate (public key)
- `hms_ultra.key` - Private key (keep secure!)

## Development Certificates

These are **self-signed certificates** for local development only.

### Important Notes

⚠️ **WARNING**: These certificates are for development use only!

- Browser will show security warnings
- Not suitable for production
- Generated for `localhost` domain only

### Usage

The certificates are automatically mounted into the nginx container at `/etc/nginx/ssl/` and used by the nginx configuration.

### Regeneration

To regenerate the certificates:

```bash
# From project root
cd scripts/deployment/
./generate-ssl-certs.sh

# Or manually
openssl req -x509 -newkey rsa:4096 \
  -keyout config/ssl/hms_ultra.key \
  -out config/ssl/hms_ultra.crt \
  -days 365 -nodes \
  -subj "/C=US/ST=State/L=City/O=HMS Ultra/OU=IT Department/CN=localhost"
```

## Production

For production deployment, replace these certificates with:

1. **Let's Encrypt certificates** (free, automated)
2. **Commercial CA certificates** (purchased)
3. **Internal CA certificates** (enterprise)

## Security

- Private key (`hms_ultra.key`) has restricted permissions (600)
- Certificate (`hms_ultra.crt`) has read permissions (644)
- Never commit private keys to version control
- Rotate certificates regularly

## Troubleshooting

### Certificate Issues
```bash
# Check certificate validity
openssl x509 -in hms_ultra.crt -dates -noout

# Test certificate
openssl x509 -in hms_ultra.crt -text -noout
```

### Permission Issues
```bash
# Fix permissions
chmod 600 hms_ultra.key
chmod 644 hms_ultra.crt
```

## Documentation

For detailed setup instructions, see:
- `docs/deployment/NGINX_SSL_SETUP.md`
- `docs/deployment/SECURITY_SETUP.md`

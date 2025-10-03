#!/bin/bash
# Generate SSL certificates for HMS Ultra development
# This script creates self-signed certificates for local development

set -e

SSL_DIR="../config/ssl"
CERT_FILE="hms_ultra.crt"
KEY_FILE="hms_ultra.key"

echo "Generating SSL certificates for HMS Ultra development..."

# Create ssl directory if it doesn't exist
mkdir -p "$SSL_DIR"

# Generate private key
echo "Generating private key..."
openssl genrsa -out "$SSL_DIR/$KEY_FILE" 2048

# Generate certificate signing request
echo "Generating certificate signing request..."
openssl req -new -key "$SSL_DIR/$KEY_FILE" -out "$SSL_DIR/hms_ultra.csr" -subj "/C=US/ST=State/L=City/O=HMS Ultra/OU=IT Department/CN=localhost"

# Generate self-signed certificate
echo "Generating self-signed certificate..."
openssl x509 -req -days 365 -in "$SSL_DIR/hms_ultra.csr" -signkey "$SSL_DIR/$KEY_FILE" -out "$SSL_DIR/$CERT_FILE"

# Set proper permissions
chmod 600 "$SSL_DIR/$KEY_FILE"
chmod 644 "$SSL_DIR/$CERT_FILE"

# Clean up CSR file
rm "$SSL_DIR/hms_ultra.csr"

echo "SSL certificates generated successfully!"
echo "Certificate: $SSL_DIR/$CERT_FILE"
echo "Private Key: $SSL_DIR/$KEY_FILE"
echo ""
echo "⚠️  WARNING: These are self-signed certificates for development only!"
echo "   For production, use certificates from a trusted Certificate Authority."
echo ""
echo "To use these certificates in nginx, update your nginx.conf:"
echo "  ssl_certificate     /etc/nginx/ssl/$CERT_FILE;"
echo "  ssl_certificate_key /etc/nginx/ssl/$KEY_FILE;"

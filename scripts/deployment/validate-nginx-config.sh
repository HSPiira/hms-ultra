#!/bin/bash
# Validate nginx configuration structure
# This script checks if the nginx.conf file has the required structure

set -e

NGINX_CONFIG="config/nginx/nginx.conf"

echo "Validating nginx configuration..."

# Check if file exists
if [ ! -f "$NGINX_CONFIG" ]; then
    echo "❌ ERROR: nginx.conf file not found at $NGINX_CONFIG"
    exit 1
fi

echo "✅ nginx.conf file found"

# Check for events block
if grep -q "events {" "$NGINX_CONFIG"; then
    echo "✅ events block found"
else
    echo "❌ ERROR: events block missing"
    exit 1
fi

# Check for http block
if grep -q "http {" "$NGINX_CONFIG"; then
    echo "✅ http block found"
else
    echo "❌ ERROR: http block missing"
    exit 1
fi

# Check for worker_connections
if grep -q "worker_connections" "$NGINX_CONFIG"; then
    echo "✅ worker_connections configured"
else
    echo "❌ ERROR: worker_connections not configured"
    exit 1
fi

# Check for server block
if grep -q "server {" "$NGINX_CONFIG"; then
    echo "✅ server block found"
else
    echo "❌ ERROR: server block missing"
    exit 1
fi

# Check for upstream configuration
if grep -q "upstream web" "$NGINX_CONFIG"; then
    echo "✅ upstream web configuration found"
else
    echo "❌ ERROR: upstream web configuration missing"
    exit 1
fi

# Check for proxy_pass
if grep -q "proxy_pass" "$NGINX_CONFIG"; then
    echo "✅ proxy_pass configuration found"
else
    echo "❌ ERROR: proxy_pass configuration missing"
    exit 1
fi

echo ""
echo "🎉 nginx configuration validation passed!"
echo ""
echo "Configuration summary:"
echo "- Events block: ✅"
echo "- HTTP block: ✅"
echo "- Server block: ✅"
echo "- Upstream configuration: ✅"
echo "- Proxy configuration: ✅"
echo ""
echo "The nginx configuration is ready for deployment."

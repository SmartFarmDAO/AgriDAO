#!/bin/bash
mkdir -p ssl
if [ ! -f ssl/cert.pem ]; then
    echo "Generating self-signed certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout ssl/key.pem \
      -out ssl/cert.pem \
      -subj "/C=US/ST=State/L=City/O=AgriDAO/OU=IT/CN=agridao.com"
    chmod 644 ssl/cert.pem
    chmod 600 ssl/key.pem
    echo "Certificate generated in ssl/"
else
    echo "Certificate already exists in ssl/"
fi

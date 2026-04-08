#!/bin/sh

# Replace environment variables in nginx template
# We replace the template we defined with the default conf file that
# NGINX uses to build the actual nginx.conf that it uses
envsubst '$FULLSTACK_API_URL' < /etc/nginx/templates/nginx.conf.template > /etc/nginx/conf.d/default.conf

cat << EOF > /usr/share/nginx/html/env.js
window.env = {
  FULLSTACK_API_URL: "$FULLSTACK_API_URL",
  VERSION: "$VITE_VERSION",
  GOOGLE_CLIENT_ID: "$GOOGLE_CLIENT_ID",
  LOGIN_REDIRECT_URL: "$LOGIN_REDIRECT_URL",
};
EOF

# Execute the CMD from the Dockerfile
exec nginx -g 'daemon off;'

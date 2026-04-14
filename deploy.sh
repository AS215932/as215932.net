#!/usr/bin/env bash
# Deploy the as215932.net static site to the web VM.
#
# Syncs *.html and style.css to /var/www/as215932.net/ on the web VM
# and reloads nginx. The nginx server block and Caddy vhost are managed
# in the hyrule-infra repository, not here.

set -euo pipefail

WEB_HOST=${WEB_HOST:-2a0c:b641:b50:2::30}
WEB_USER=${WEB_USER:-root}
WEB_PATH=${WEB_PATH:-/var/www/as215932.net/}
SSH_KEY=${SSH_KEY:-$HOME/.ssh/id_servify}

HERE=$(cd "$(dirname "$0")" && pwd)

echo ">> rsync $HERE -> $WEB_USER@[$WEB_HOST]:$WEB_PATH"
rsync -av --delete \
    --include='*.html' --include='style.css' \
    --exclude='*' \
    -e "ssh -i $SSH_KEY" \
    "$HERE/" "$WEB_USER@[$WEB_HOST]:$WEB_PATH"

echo ">> chown + nginx reload"
ssh -i "$SSH_KEY" "$WEB_USER@$WEB_HOST" \
    "chown -R www-data:www-data $WEB_PATH && nginx -t && systemctl reload nginx"

echo ">> smoke test"
curl -6 -sfI https://as215932.net/ | head -1

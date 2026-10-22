#!/usr/bin/env bash
# Push the built pages to the web server over ssh. Settings in .env.local (see .env.example).
set -e
cd "$(dirname "$0")/.."
[ -f .env.local ] && . ./.env.local
: "${DEPLOY_HOST:?set DEPLOY_HOST in .env.local}"; : "${DEPLOY_USER:?set DEPLOY_USER in .env.local}"; : "${DEPLOY_PATH:?set DEPLOY_PATH in .env.local}"
KEY="${DEPLOY_KEY:-$HOME/.ssh/id_ed25519}"
case "$KEY" in "~/"*) KEY="$HOME/${KEY#\~/}" ;; esac
SRC="$(cd ../prototypes && pwd)/"
echo "deploying $SRC -> $DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH"
# --delete keeps the server equal to the build; the sealed archive, READMEs, lock.py and root landing files are preserved
rsync -az --delete --exclude 'README.md' --exclude 'lock.py' --exclude 'archive/' --exclude '__pycache__' --exclude '/index.html' --exclude '/img/' \
  -e "ssh -i \"$KEY\" -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
  "$SRC" "$DEPLOY_USER@$DEPLOY_HOST:$DEPLOY_PATH/"
echo "deployed"

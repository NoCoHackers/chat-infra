#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${DEPLOY_EXTRA_VARS_FILE:?Absolute path to protected JSON/YAML secret variables required}"
test -f "$DEPLOY_EXTRA_VARS_FILE"
revision="$(tr -d '\n' < upstream-revision)"
[[ "$revision" =~ ^[0-9a-f]{40}$ ]] || { echo "Invalid upstream revision"; exit 1; }
mkdir -p .work
if [[ ! -d .work/mdad/.git ]]; then
  git init .work/mdad
  git -C .work/mdad remote add origin https://github.com/spantaleev/matrix-docker-ansible-deploy.git
fi
git -C .work/mdad fetch --depth 1 origin "$revision"
git -C .work/mdad checkout --detach FETCH_HEAD
test "$(git -C .work/mdad rev-parse HEAD)" = "$revision"
rm -rf .work/mdad/inventory
cp -R inventory .work/mdad/inventory
cd .work/mdad
ansible-galaxy install -r requirements.yml -p roles/galaxy/ --force
ansible-playbook -i inventory/hosts setup.yml --syntax-check --extra-vars "@$DEPLOY_EXTRA_VARS_FILE"
if [[ "${SYNTAX_ONLY:-false}" != true ]]; then
  ansible-playbook -i inventory/hosts ../../element-icons.yml
  ansible-playbook -i inventory/hosts setup.yml --tags=setup-all,start --extra-vars "@$DEPLOY_EXTRA_VARS_FILE"
fi

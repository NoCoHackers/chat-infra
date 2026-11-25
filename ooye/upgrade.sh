#!/usr/bin/env bash
# Run as root on the droplet after a verified offsite backup.
set -euo pipefail
umask 077
[[ $# == 3 && $1 =~ ^v[0-9]+\.[0-9]+(\.[0-9]+)?$ && $2 =~ ^[a-f0-9]{40}$ && $3 =~ ^22\.[0-9]+\.[0-9]+$ ]]
tag=$1 revision=$2 node=$3
live=/var/lib/noco-ooye
runtime=/opt/noco-node
exec 9>/run/lock/noco-ooye-upgrade.lock
flock -n 9
systemctl is-active --quiet noco-ooye
as_ooye() { runuser -u ooye -- "$@"; }
current=$(as_ooye git -C "$live" rev-parse HEAD)
current_node=$("$runtime/bin/node" -p 'process.versions.node')
[[ $current != "$revision" || $current_node != "$node" ]] || exit 0
[[ $(uname -m) == x86_64 ]]
# Ignore the lockfile changes made by the original npm install, not other edits.
test -z "$(as_ooye git -C "$live" status --porcelain --untracked-files=no -- . ':!package-lock.json')"
stage=$(mktemp -d /var/lib/.noco-ooye-upgrade.XXXXXX)
trap 'rm -rf -- "$stage"' EXIT
chmod 0711 "$stage"
install -d -m 0755 "$stage/node"
install -d -m 0700 -o ooye -g ooye "$stage/src"
archive=node-v${node}-linux-x64.tar.xz
if [[ $current_node != "$node" ]]; then
  curl -fsS --retry 3 --max-time 90 "https://nodejs.org/dist/v$node/SHASUMS256.txt" -o "$stage/SHASUMS256.txt"
  curl -fsS --retry 3 --max-time 120 "https://nodejs.org/dist/v$node/$archive" -o "$stage/$archive"
  (cd "$stage"; grep -F "  $archive" SHASUMS256.txt | sha256sum --check --strict -)
  tar -xJf "$stage/$archive" --strip-components=1 -C "$stage/node"
  node_bin=$stage/node/bin
else
  node_bin=$runtime/bin
fi
as_ooye git clone --quiet --depth 1 --branch "$tag" https://gitdab.com/cadence/out-of-your-element.git "$stage/src"
test "$(as_ooye git -C "$stage/src" rev-parse HEAD)" = "$revision"
(cd "$stage/src"; as_ooye env "PATH=$node_bin:/usr/bin:/bin" npm ci --no-audit --no-fund)
# Make the verified commit available locally before stopping the live service.
as_ooye git -C "$live" fetch --no-tags "$stage/src" HEAD
test "$(as_ooye git -C "$live" rev-parse FETCH_HEAD)" = "$revision"
previous=$(mktemp -d /var/lib/.noco-ooye-previous.XXXXXX)
systemctl stop noco-ooye
# Preserve the prior runtime and deps for operator recovery. Do not roll back a migrated DB automatically.
if [[ $current_node != "$node" ]]; then
  mv -T "$runtime" "$previous/node"
  mv -T "$stage/node" "$runtime"
fi
as_ooye git -C "$live" restore --source=HEAD --worktree --staged -- package-lock.json
as_ooye git -C "$live" switch --detach "$revision"
mv -T "$live/node_modules" "$previous/node_modules"
mv -T "$stage/src/node_modules" "$live/node_modules"
# The registration and SQLite database remain in the live working directory.
chmod -R a+rX "$runtime"
systemctl start noco-ooye
printf 'OOYE %s and Node %s installed; previous files: %s\n' "$tag" "$node" "$previous"

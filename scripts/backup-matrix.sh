#!/usr/bin/env bash
set -euo pipefail
umask 077
work=/run/noco-matrix-backup/staging
mkdir -m 0700 "$work"
trap 'rm -rf -- "$work"' EXIT
cd "$work"
docker exec matrix-postgres sh -ec 'exec pg_dumpall -U "$POSTGRES_USER"' >postgres.sql
test -s postgres.sql
python3 - <<'PY'
import sqlite3
from contextlib import closing
with closing(sqlite3.connect('file:/var/lib/noco-ooye/ooye.db?mode=ro', uri=True)) as src, closing(sqlite3.connect('ooye.db')) as dst:
    src.backup(dst)
    if dst.execute('PRAGMA quick_check').fetchone() != ('ok',):
        raise SystemExit('OOYE backup failed integrity check')
PY
# The database dumps must succeed before backup.
restic backup --group-by host,tags --tag matrix-nightly . \
  /matrix/synapse/config /matrix/synapse/storage \
  /var/lib/noco-ooye/registration.yaml /etc/noco-ooye \
  /etc/systemd/system/noco-ooye.service /etc/systemd/system/noco-ooye-firewall.service
restic forget --group-by host,tags --tag matrix-nightly --keep-daily 7 --keep-weekly 4 --keep-monthly 6

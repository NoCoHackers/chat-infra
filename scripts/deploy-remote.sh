#!/usr/bin/env bash
set -euo pipefail
case "${1:-}" in
  backup) command='systemctl start noco-matrix-backup.service' ;;
  start) command="/usr/local/sbin/noco-maintenance-notice message 'A reviewed Matrix stack update is starting. The offsite backup succeeded; chat may briefly be unavailable.

The Enrichment Center apologizes for the inconvenience and wishes you the best of luck.'" ;;
  upgrade-bridge)
    repo=$(cd -- "$(dirname -- "$0")/.." && pwd)
    pins=$(python3 -c 'import json,re,sys; d=json.load(open(sys.argv[1])); values=[d[k] for k in ("tag","commit","node")]; assert all(re.fullmatch(p,v) for p,v in zip((r"v[0-9]+\.[0-9]+(?:\.[0-9]+)?",r"[a-f0-9]{40}",r"22\.[0-9]+\.[0-9]+"),values)); print(*values)' "$repo/ooye/versions.json")
    command="bash -s -- $pins"
    exec < "$repo/ooye/upgrade.sh"
    ;;
  check-bridge) command='systemctl is-active --quiet noco-ooye.service' ;;
  complete) command="/usr/local/sbin/noco-maintenance-notice message 'Matrix stack update complete. Synapse, Element Web, and the bridge are responding.

For science. You monster.'" ;;
  failed) command="/usr/local/sbin/noco-maintenance-notice message 'The Matrix update workflow did not complete successfully. An organizer should check the deployment logs.

The Enrichment Center apologizes for this clearly broken test chamber.'" ;;
  *) echo 'Usage: deploy-remote.sh backup|start|upgrade-bridge|check-bridge|complete|failed' >&2; exit 2 ;;
esac
exec ssh -i "$HOME/.ssh/matrix_deploy" -o BatchMode=yes -o StrictHostKeyChecking=yes -o IdentitiesOnly=yes -o ConnectTimeout=10 root@matrix.nocohackers.com "$command"

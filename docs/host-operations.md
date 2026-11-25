# Host maintenance and backups

From the infra repo root, use the same verified SSH access as the Matrix deployment:

```sh
ansible-playbook -i inventory/hosts host-patching.yml
ansible-playbook -i inventory/hosts host-backup.yml
ansible-playbook -i inventory/hosts host-reboot.yml
```

On a rebuild, provision root-only `/etc/noco-matrix-backup/spaces.env` and `restic-password`, and optional `heartbeat.env`, separately. Reuse the existing Restic repository and password for recovery; initialize only a new repository. Once credentials and repository are ready, apply `host-backup.yml -e noco_enable_backup_timer=true`. Staging alone does not change the timer's enablement. The backup job expects Synapse, PostgreSQL and OOYE to already be installed at their production paths.

Provision `/etc/noco-maintenance/matrix-token` separately with mode `0600`, and verify the GLaDOS account can post to the announcements room before enabling the maintenance schedule on a rebuild. Apply `host-reboot.yml` after backups are working. The playbook installs `noco-maintenance-notice` and `noco-reboot` without invoking them. The weekly timer is conditional on Ubuntu requesting a reboot. For manual maintenance, invoke `noco-reboot` explicitly as root; `--without-notice` is for emergencies only.

OOYE's runtime installation, interactive setup, firewall and registration remain separate from these playbooks.

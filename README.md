# NoCo Hackers Chat Infra

Matrix configuration for NoCo Hackers. Many of the challenging components are handled by [matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy).

- Mailjet for signup verification and password-reset email.
- Namecheap for DNS and domain registration.
- The [NoCo Hackers website](https://github.com/NoCoHackers/NoCoHackers.github.io), hosted on Amplify, serves Matrix client and federation discovery.
- Nightly encrypted Restic backups to DigitalOcean Spaces at 09:00 UTC, with up to 20 minutes of jitter. Healthchecks.io alerts on missed successful backups; it is not a Matrix uptime monitor.
- [OOYE](https://gitdab.com/cadence/out-of-your-element) bridges Discord and Matrix.
- Ansible manages the Matrix stack and host maintenance. Ubuntu security updates are unattended. The host reboots on Sundays at 12:00 UTC.
- The [GitHub Actions update workflow](docs/upstream-updates.md) checks for upstream changes Mondays at 09:00 UTC and proposes pin updates for review once enabled in GitHub.

Currently hosted on a DigitalOcean droplet with 2 GB RAM, 2 vCPUs, and 60 GB of disk.

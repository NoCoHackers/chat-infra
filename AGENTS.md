# Agent instructions: NoCo Hackers Matrix infrastructure

Text-first, publicly joinable community chat. Identities use nocohackers.com; Amplify continues hosting the website.

**Scaffold only: not yet deployed or integration-tested.** See [bootstrap](docs/bootstrap.md).
`upstream-revision` pins a commit of the upstream Ansible playbook, not a Matrix protocol version. The playbook supplies the default container image versions (including Synapse); inspect those defaults and the upstream changelog before updating the pin.
Use the DigitalOcean droplet and upstream Ansible playbook; keep k3s for experimentation. Do not deploy or change DNS without operator approval. Keep credentials out of Git and logs.

The deployment key has root access: treat repository workflow modification as privileged server access.

## Local syntax check

Use Python 3.11+ in a virtual environment with ansible-core==2.19.3 installed.
Set DEPLOY_EXTRA_VARS_FILE to an absolute path outside Git containing the two required persistent secrets.
Run: SYNTAX_ONLY=true bash scripts/deploy.sh

This downloads upstream dependencies but does not connect to or change the droplet.

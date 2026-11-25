# Bootstrap checklist

1. Create a private NoCoHackers/nocohackers-chat-infra repository; protect main and review changes to workflows and inventory. GitHub Actions runs secret-free CI on pull requests and main pushes (.github/workflows/ci.yml): shell syntax, YAML/JSON parsing, pinned revision, and public-signup/email-verification configuration checks. Require the validate job in branch protection once it has run. Deployment is a separate manually triggered Actions workflow (.github/workflows/deploy-matrix.yml); PR CI never gets production credentials or accesses the droplet. These static checks do not replace a full Ansible syntax check or deployed integration tests.
2. Provision a 2 GB Ubuntu 24.04 LTS droplet with your operator SSH key.
3. Add matrix.nocohackers.com and chat.nocohackers.com A records to its IPv4. Leave the apex DNS on Amplify. Do not add AAAA yet.
4. Allow public TCP 80/443. Choose and document SSH exposure: this scaffold uses public key-only SSH for GitHub-hosted runners. Their IPs vary. If using an overlay, modify the workflow before deployment. Disable password SSH only after testing operator key access; retain provider console recovery.
5. Generate a dedicated, unencrypted CI SSH key locally, protect its private key, and install only its public key in root's authorized_keys. This deliberately grants the upstream playbook its required root access. Keep operator keys separate.
6. Verify the host key through the provider console or another trusted channel. Store an OpenSSH known_hosts line for matrix.nocohackers.com. ssh-keyscan alone is not trusted verification.
7. Create the production GitHub environment. Configure main-only deployment and required reviewer approval if your GitHub plan supports private-repository environment protection. Otherwise agree a manual approval alternative before adding secrets.
8. Set environment secrets:
   - MATRIX_SSH_PRIVATE_KEY: dedicated CI private key.
   - MATRIX_SSH_KNOWN_HOSTS: independently verified hostname/key line.
   - MATRIX_EXTRA_VARS_JSON: JSON object with matrix_homeserver_generic_secret_key and postgres_connection_password, each generated independently using a password manager or openssl rand -hex 32. Persist these values: do not regenerate per deployment.
   - Also include matrix_synapse_email_smtp_host, matrix_synapse_email_smtp_user, matrix_synapse_email_smtp_pass, and matrix_synapse_email_notif_from (a provider-verified sender such as NoCo Hackers <matrix@nocohackers.com>). For Mailjet use `in-v3.mailjet.com` with STARTTLS on port 2525, the API key as SMTP username and the secret key as SMTP password; configure the provider's required DNS sender verification/SPF/DKIM records. SMTP credentials stay in this secret, not Git.
   - Add traefik_config_certificatesResolvers_acme_email to that JSON with a monitored operator email after verifying the setting against pinned upstream.
9. Inspect upstream defaults, current security notices, and the selected component list. Confirm any additional default-enabled services are acceptable before first deployment.
10. Push to main and manually run Deploy Matrix. Diagnose failures without pasting secrets into chat.
11. Copy website/static contents into the Hugo repo's static directory. Merge website/customHttp.yml into existing Amplify headers (do not blindly overwrite). Publish when the homeserver is ready. Verify both apex discovery paths return 200 JSON and client CORS headers, not HTML.
12. Create the first server-admin account using upstream docs/registering-users.md. Do not store its password in inventory or Actions logs. Server administration and room power levels are distinct.
13. Create a public NoCo Hackers Space and public rooms: announcements, general, projects, help. Assign stable aliases, publish matrix.to links, restrict room/Space admin and moderation permissions, and explicitly select history visibility. Public access is intentional; do not make initial rooms invite-only.
14. Test in public from day one: anyone can create a local account after email verification, without an invite or registration token. Configure SMTP before testing signup; verify delivery, verification links, and password recovery from a real external mailbox. Confirm signup cannot complete without verification. Email verification is not complete spam protection: retain upstream rate limits, monitor account growth/disk usage, and be ready to suspend abuse or temporarily pause registration. Federated existing accounts can join public rooms independently of local signup. Confirm new accounts have no server-admin or privileged room/Space permissions.
15. Test with ordinary local and remote accounts, mobile notifications, public joining and denied administrative actions. Confirm deployed features with chosen clients; modern mobile clients may require a separately evaluated authentication setup. Do not promise Element X compatibility without testing.
16. Invite regulars with an experimental-service/history-loss notice. Backups, recovery exercises, and second-operator onboarding can proceed in parallel, per the reviewed plan.

## Security and recovery follow-ups

- Set upload/media retention limits and disk/service alerts.
- Configure encrypted off-server backups of consistent PostgreSQL dumps, media, configuration/secrets, and Synapse signing keys; save credentials outside this droplet and GitHub.
- Test isolated restore without allowing a duplicate production identity onto the network.
- Give a second operator independent recovery access; record domain/provider ownership and billing contacts.
- Back up before upgrades. Reverting upstream revisions is not a safe database rollback strategy.
- Never delete /matrix or regenerate signing keys to fix a failed deployment.

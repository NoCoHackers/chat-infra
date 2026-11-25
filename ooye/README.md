# OOYE pilot — staged, not deployed

Use upstream's [interactive installation](https://gitdab.com/cadence/out-of-your-element/src/tag/v3.8.2/docs/for-hosters/install.md). Proposed pin: `v3.8.2`, tag ref `826cd63a8ee4e4457a23bfd2dc826f328986daf2`; verify tag and review release before installation. Use Node.js 22+; verify `/usr/bin/npm` and the Node version before enabling the supplied systemd unit. Install and run setup as a dedicated unprivileged `ooye` user in `/var/lib/noco-ooye` (directory mode 0700); keep generated config, registration and SQLite state out of Git. Enter Discord credentials only in the setup session.

## Network and registration (verify on the droplet before applying)

- Add `bridge.nocohackers.com` DNS and use the existing Traefik for HTTPS. Configure a router for this hostname only. Check the pinned Traefik role's supported dynamic config mechanism and existing TLS resolver before installing the route.
- Use a Docker-reachable private host address for OOYE's listener and registration URL: both Traefik and Synapse must reach it from their respective networks. Do not use container localhost for a host service. Verify the actual bridge addresses and source subnets, allow only the necessary local container traffic to OOYE's TCP 6693, and verify 6693 is unreachable from the public internet. Do not route Matrix appservice transaction paths through the public UI hostname.
- Run `npm run setup` interactively once the HTTPS route works. Stage the generated registration in Synapse's mounted config directory with access limited to Synapse and operators. Add its container path to MDAD's `matrix_synapse_app_service_config_files` without replacing other registrations. Both appservice tokens are secrets. Back up the previous configuration and schedule a brief Synapse restart; verify normal client and federation health afterwards before linking channels.

## Pilot and rollback

- Start the bridge with systemd and inspect `journalctl -u noco-ooye`. Install the bot using OOYE and select Self Service mode. Link one agreed channel to one existing room, communicate the relay in both places, and test both directions, media and moderation. Do not link private channels to public rooms.
- Compare `sar -r` and `sar -W` before and after, and inspect for OOM kills. Sustained swapping or chat lag means pause and reassess capacity.
- If needed, stop OOYE, unlink the test channel, remove the appservice from Synapse config and restart Synapse, then remove the Traefik route. Retain protected state for recovery until the pilot's disposition is decided.

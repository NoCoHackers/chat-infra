"""Secret-free static checks; does not contact or deploy to the server."""
import json
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
for pattern in (".github/workflows/*.yml", "inventory/host_vars/*/*.yml", "website/*.yml"):
    for path in ROOT.glob(pattern):
        # BaseLoader preserves workflow's 'on' key instead of YAML 1.1 boolean coercion.
        document = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
        assert isinstance(document, dict), f"Expected mapping: {path}"
        print(f"YAML OK: {path.relative_to(ROOT)}")

revision = (ROOT / "upstream-revision").read_text().strip()
assert re.fullmatch(r"[0-9a-f]{40}", revision), "Upstream must be pinned to a commit"
config = yaml.safe_load((ROOT / "inventory/host_vars/matrix.nocohackers.com/vars.yml").read_text())
assert config["matrix_domain"] == "nocohackers.com"
assert config["matrix_synapse_enable_registration"] is True
assert config["matrix_synapse_enable_registration_without_verification"] is False
assert config["matrix_synapse_registrations_require_3pid"] == ["email"]
assert config["matrix_synapse_email_enabled"] is True
assert config["matrix_synapse_email_smtp_require_transport_security"] is True
assert config["matrix_static_files_container_labels_base_domain_enabled"] is False

base = ROOT / "website/static/.well-known/matrix"
server = json.loads((base / "server").read_text())
client = json.loads((base / "client").read_text())
assert server["m.server"] == "matrix.nocohackers.com:443"
assert client["m.homeserver"]["base_url"] == "https://matrix.nocohackers.com"
print("Configuration policy and discovery checks passed")

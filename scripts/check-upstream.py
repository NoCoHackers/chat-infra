#!/usr/bin/env python3
"""Report upstream candidates, or update local pins with --apply."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
MDAD = 'https://github.com/spantaleev/matrix-docker-ansible-deploy'
OOYE = 'https://gitdab.com/cadence/out-of-your-element'


def refs(url, *patterns):
    out = subprocess.check_output(['git', 'ls-remote', url + '.git', *patterns], text=True, timeout=60)
    return {ref: sha for sha, ref in map(str.split, out.splitlines()) if re.fullmatch('[a-f0-9]{40}', sha)}


def version(tag):
    return tuple(int(x) for x in tag.lstrip('v').split('.'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    pin = ROOT / 'upstream-revision'
    versions = ROOT / 'ooye/versions.json'
    old = pin.read_text().strip()
    ooye = json.loads(versions.read_text())
    head = refs(MDAD, 'HEAD')['HEAD']
    tags = refs(OOYE, 'refs/tags/v*')
    tag = max((r.removeprefix('refs/tags/') for r in tags if re.fullmatch(r'refs/tags/v\d+\.\d+(?:\.\d+)?', r)), key=version)
    ref = 'refs/tags/' + tag
    commit = tags.get(ref + '^{}', tags[ref])
    with urlopen('https://nodejs.org/dist/index.json', timeout=30) as response:
        node = max((r['version'][1:] for r in json.load(response) if re.fullmatch(r'v22\.\d+\.\d+', r['version']) and 'linux-x64' in r['files']), key=version)
    if tag == ooye['tag'] and commit != ooye['commit']:
        raise SystemExit('Pinned OOYE tag moved; investigate manually.')
    if head != old:
        print(f'- [MDAD upstream comparison]({MDAD}/compare/{old}...{head}) (default-branch tip; upstream has no release tags). Review image changes, especially PostgreSQL major versions, and recheck Element icon paths.')
    if version(tag) > version(ooye['tag']):
        print(f'- OOYE: {ooye["tag"]} → [{tag}]({OOYE}/releases/tag/{tag})')
        ooye.update(tag=tag, commit=commit)
    if version(node) > version(ooye['node']):
        print(f'- Node.js: {ooye["node"]} → [{node}](https://nodejs.org/en/blog/release/v{node}) (stay on major 22)')
        ooye['node'] = node
    if args.apply:
        pin.write_text(head + '\n')
        versions.write_text(json.dumps(ooye, indent=2) + '\n')


if __name__ == '__main__':
    main()

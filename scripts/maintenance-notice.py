#!/usr/bin/env python3
import json
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

BASE = 'https://matrix.nocohackers.com'
ROOM = '!ADdbg4_VQRucZRceD_83nTyEuJUDtxdim7tDUrJ-aXw'
TOKEN = Path('/etc/noco-maintenance/matrix-token')
MARKER = Path('/var/lib/noco-maintenance/pending')
BOOT = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
GLADOS_QUOTE = 'Por favor bordón de fallar Muchos gracias de fallar gracias'
COMPLETION_QUOTE = 'All NoCo Hackers technologies remain safely operational up to 4000 degrees Kelvin'


def request(url, *, data=None, auth=False):
    headers = {'Content-Type': 'application/json'}
    if auth:
        headers['Authorization'] = 'Bearer ' + TOKEN.read_text().strip()
    with urlopen(Request(url, data=data, headers=headers,
                         method='PUT' if data else 'GET'), timeout=10) as response:
        return response.read()


def send(text, txn):
    url = f'{BASE}/_matrix/client/v3/rooms/{quote(ROOM, safe="")}/send/m.room.message/{txn}'
    result = json.loads(request(url, auth=True, data=json.dumps({
        'msgtype': 'm.notice', 'body': text,
    }).encode()))
    if not result.get('event_id'):
        raise ValueError('No event ID')


def main(mode):
    if mode == 'test':
        send('GLaDOS maintenance notifier test. No reboot is scheduled by this test.', uuid.uuid4().hex)
    elif mode == 'message':
        send(sys.argv[2], uuid.uuid4().hex)
    elif mode in ('start', 'manual'):
        message = ('The Matrix server is going down for a reboot NOW.' if mode == 'manual'
                   else 'Scheduled maintenance is starting. Matrix will be briefly unavailable.')
        send(message + '\n\n' + GLADOS_QUOTE, mode + '-' + BOOT)
        tmp = MARKER.with_suffix('.tmp')
        tmp.write_text(BOOT)
        tmp.replace(MARKER)
    elif mode == 'end' and MARKER.exists():
        previous = MARKER.read_text().strip()
        if previous != BOOT:
            request(BASE + '/_matrix/client/versions')
            request('https://chat.nocohackers.com/config.json')
            request('https://bridge.nocohackers.com/')
            send('Maintenance complete. Matrix, Element Web, and the bridge are responding.\n\n' + COMPLETION_QUOTE, 'end-' + previous)
            MARKER.unlink()


try:
    main(sys.argv[1])
except HTTPError as exc:
    sys.exit(f'Maintenance notifier: HTTP {exc.code}')
except (OSError, ValueError) as exc:
    sys.exit(f'Maintenance notifier: {type(exc).__name__}')

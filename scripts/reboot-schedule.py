#!/usr/bin/env python3
"""One-off UTC maintenance schedule; invoked as root by CLI and timer."""
import fcntl
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/var/lib/noco-maintenance')
STATE = ROOT / 'scheduled-reboot.json'
NOTICE = '/usr/local/sbin/noco-maintenance-notice'


def run(*args):
    subprocess.run(args, check=True)


def save(data):
    tmp = STATE.with_suffix('.tmp')
    tmp.write_text(json.dumps(data))
    tmp.replace(STATE)


def notify(text):
    run(NOTICE, 'message', text)


def main(args):
    state = json.loads(STATE.read_text()) if STATE.exists() else None
    now = time.time()
    if len(args) == 2 and args[0] == 'schedule':
        if state:
            sys.exit('A reboot is already scheduled; cancel it first.')
        date = datetime.strptime(args[1], '%Y-%m-%d %H:%M UTC').replace(tzinfo=timezone.utc)
        if date.timestamp() - now < 300:
            sys.exit('Specify a UTC time at least five minutes in the future.')
        notify(f'Matrix reboot scheduled for {args[1]}.')
        save(dict(at=date.timestamp(), label=args[1], ready=False))
        print(f'Scheduled: {args[1]}')
    elif args == ['status']:
        print(state['label'] if state else 'No one-off reboot scheduled.')
    elif args == ['cancel']:
        if not state:
            sys.exit('No one-off reboot scheduled.')
        STATE.unlink()
        notify(f'Matrix reboot scheduled for {state["label"]} was canceled.')
    elif args == ['tick']:
        if not state:
            return
        delta = state['at'] - now
        if delta < -60 or (delta <= 0 and not state['ready']):
            STATE.unlink()
            notify(f'Matrix reboot scheduled for {state["label"]} was skipped: the maintenance deadline was missed or backup was not confirmed.')
        elif delta <= 0:
            STATE.unlink()
            run('/usr/local/sbin/noco-reboot')
        elif delta <= 300 and not state['ready']:
            notify(f'Matrix reboot in about five minutes ({state["label"]}).')
            try:
                run('/usr/bin/systemctl', 'start', 'noco-matrix-backup.service')
            except subprocess.CalledProcessError:
                STATE.unlink()
                notify(f'Matrix reboot scheduled for {state["label"]} was skipped: backup failed.')
                return
            state['ready'] = True
            save(state)
    else:
        sys.exit('Usage: noco-reboot schedule "YYYY-MM-DD HH:MM UTC" | status | cancel')


if __name__ == '__main__':
    with (ROOT / 'schedule.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            main(sys.argv[1:])
        except ValueError:
            sys.exit('Invalid schedule. Use YYYY-MM-DD HH:MM UTC.')

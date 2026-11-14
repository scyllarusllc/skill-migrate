#!/usr/bin/env python3
"""Read-only integrity, schema, size, and hash check for a Pastebloom SQLite backup."""

import argparse
import hashlib
import sqlite3
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    args = parser.parse_args()
    snapshot = args.snapshot.resolve(strict=True)
    digest = hashlib.sha256()
    with snapshot.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    db = sqlite3.connect(f'file:{snapshot}?mode=ro&immutable=1', uri=True)
    try:
        result = db.execute('PRAGMA integrity_check').fetchone()[0]
        if result != 'ok':
            raise SystemExit(f'Integrity check failed: {result}')
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        required = {'blooms', 'reports', 'reviewer_sessions'}
        if not required <= tables:
            raise SystemExit('Missing required tables: ' + ', '.join(sorted(required - tables)))
        counts = {name: db.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0] for name in sorted(required)}
    finally:
        db.close()
    print(f'Backup: {snapshot}')
    print(f'Size: {snapshot.stat().st_size} bytes')
    print(f'SHA-256: {digest.hexdigest()}')
    print('Integrity: ok')
    for name, count in counts.items():
        print(f'{name}: {count}')


if __name__ == '__main__':
    main()

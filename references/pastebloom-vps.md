# Pastebloom VPS transfer

This runbook is for moving the current Docker Compose deployment to another VPS. It does not import old Frappe data. Paths and commands below are relative to the Pastebloom repository on each host; inspect the checked-out revision before use.

## Inventory

- Record the source and destination hostnames, SSH access, production domain, current Git commit, proxy configuration, and DNS control. Check both hosts have Docker Engine and Compose v2.
- Inspect `deploy/compose.env` privately. Recreate its settings on the destination with mode `600`: `APP_ORIGIN`, `PASTEBLOOM_PORT`, `REVIEWER_PASSWORD_HASH`, moderation/upload settings, and optional Google OAuth credentials. Keep `APP_ORIGIN` at the final HTTPS origin when testing the production configuration; the Google callback URI is `<APP_ORIGIN>/auth/google/callback`.
- Pastebloom's private data is in the Compose `data` volume at `/app/storage/pastebloom.sqlite`. Uploaded files are database blobs, so the consistent SQLite backup contains them. The repo and image contain the application code and public assets.
- The container listens on host loopback port `5150` by default. The HTTPS proxy must forward to that port, accept at least 22 MB request bodies, and never expose `/app/storage` or a backup file.

## Rehearsal

1. On the source, run `./deploy/backup.sh backups/rehearsal.sqlite`. This uses SQLite's online backup operation; copying only the live `.sqlite` file can miss WAL writes.
2. Run `python3 /path/to/skill-migrate/scripts/verify_snapshot.py backups/rehearsal.sqlite`. Transfer the snapshot over SSH to a private destination path, check its SHA-256 hash there, and keep it readable only by the migration operator. Transfer `deploy/compose.env` separately over the secure channel; never put it in Git or a public artifact.
3. Check out the intended Pastebloom revision on the destination. Build the image and start Compose without routing public traffic to it: `docker compose --env-file deploy/compose.env build`, then `docker compose --env-file deploy/compose.env up -d --wait`.
4. Run `./deploy/restore.sh backups/rehearsal.sqlite --replace` on the destination. It stops the app, validates the snapshot and required tables, replaces the database, and starts the app. Confirm `/api/health`, counts for `blooms`, `reports`, and accounts, representative public share/raw links, reviewer sign-in, and a test upload. Check logs and the HTTPS proxy behavior.

## Final copy and cutover

Stop new writes on the source through the proxy or a maintenance rule. Make a final backup with `./deploy/backup.sh`, verify and transfer it, then restore it on the destination. Compare row counts and a few known record IDs again. Route the domain to the destination only after the target is healthy and the public checks pass. Keep the source unable to accept writes while the destination is active; simultaneous writers create divergent databases.

Preserve the old VPS and backup during the observation period. If rollback is needed, stop destination writes before routing traffic back. An older image may not run against a database upgraded by a newer SeaORM migration; use the matching pre-upgrade backup when reverting image versions. Never run `docker compose down -v` as a migration step: it deletes the data volume.

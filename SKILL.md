---
name: skill-migrate
description: Move Pastebloom from one VPS to another using its Docker Compose deployment and SQLite backup/restore scripts. Use for planning, rehearsing, or carrying out a Pastebloom VPS migration; skip unrelated app migrations and routine updates.
---

# Pastebloom VPS migration

Use the Pastebloom repository, normally `/root/github/pastebloom`, as the source of truth. Read its current `deploy/README.md`, `compose.yaml`, `deploy/backup.sh`, `deploy/restore.sh`, and `deploy/compose.env.example` before acting; do not assume this skill's commands still match a later revision.

For the concrete transfer sequence and checks, read [references/pastebloom-vps.md](references/pastebloom-vps.md). Use `scripts/verify_snapshot.py` to inspect a transferred SQLite backup without changing it.

Keep the migration centered on one active writer. Rehearse on the destination with a copy, then capture a final consistent backup after source writes stop. Preserve the original VPS, its private Compose environment, and its data volume until the new VPS has passed health, data, login, upload, and public-link checks. Treat DNS/proxy cutover and source shutdown as live changes; follow the user's authorization for them. Never commit a backup or secret to Git.

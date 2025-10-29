Homelab-01 — Debian Hardening & Auth Log Parser
TL;DR

Hardened Debian: SSH keys-only, UFW default-deny, fail2ban for SSH.

Evidence: screenshots + Python parser → evidence/auth_failures.csv.

Demo: controlled fail2ban ban (for the screenshot), then reverted to safe defaults.

New: Dockerised parser — run on host /var/log (read-only) or bundled sample logs with one command.

What this repo contains

scripts/parse_authlog.py — parses /var/log/auth.log* (classic + ISO formats; IPv4/IPv6) to CSV

evidence/ — output CSV (auth_failures.csv)

screenshots/ — proof shots (fail2ban status & ban log, docker runs)

Dockerfile, docker-compose.yml, Makefile, samples/ — run parser in Docker (host or sample logs)

Reproduce (native host)
```
# SSH hardening (no passwords; no root login)
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# UFW (default deny inbound; allow SSH)
sudo apt update && sudo apt install -y ufw fail2ban rsyslog
sudo ufw default deny incoming && sudo ufw default allow outgoing
sudo ufw allow 22/tcp && sudo ufw enable
sudo systemctl enable --now fail2ban rsyslog

# Parse auth logs → CSV
python3 scripts/parse_authlog.py
ls -l evidence/auth_failures.csv && tail -n 5 evidence/auth_failures.csv
```
Docker usage
```
Parse host auth logs (Linux)
docker build -t homelab-01-parser .
docker run --rm \
  -e LOG_DIR=/var/log \
  -e OUT_PATH=/app/evidence/auth_failures.csv \
  -v /var/log:/var/log:ro \
  -v "$PWD/evidence":/app/evidence \
  homelab-01-parser

tail -n 5 evidence/auth_failures.csv

Parse bundled sample logs (Mac/Windows/Linux)
docker build -t homelab-01-parser .
docker run --rm \
  -e LOG_DIR=/app/samples \
  -e OUT_PATH=/app/evidence/auth_failures.csv \
  -v "$PWD/samples":/app/samples:ro \
  -v "$PWD/evidence":/app/evidence \
  homelab-01-parser

tail -n 5 evidence/auth_failures.csv
```

(Compose targets are also available: docker compose run --rm parser-host or parser-sample.)

Evidence (screenshots)

screenshots/fail2ban-status_banned.png — Currently banned: 1 (127.0.0.1), logpath /var/log/auth.log

screenshots/fail2ban-log_ban.png — shows Ban 127.0.0.1 in /var/log/fail2ban.log

screenshots/docker-parser_sample-run.png — container run on sample logs

screenshots/docker-parser_host-run.png — container run on host /var/log

CSV output: evidence/auth_failures.csv

Issues faced → fixes (short)

Fail2ban didn’t count failures (0 failed / 0 banned).
Cause: journal filter ignored sshd-session / localhost.
Fix: pointed jail to /var/log/auth.log, disabled ignoreself temporarily for demo, then restored defaults.

auth.log access denied when parsing.
Fix: run parser as a user in adm group or with sudo; write output to repo folder.

SSH broke after a typo in sshd_config.
Fix: tested with sshd -t before restart; kept /etc/ssh/sshd_config.bak backup.

Docker couldn’t find env vars in parser.
Fix: added import os + LOG_DIR / OUT_PATH env handling, rebuilt with --no-cache.

What I learned

Harden-first, then prove changes (screenshots + CSV).

Small parsers make noisy logs actionable; CSV is easy to triage/share.

Dockerising tools helps reviewers run them quickly (host logs vs sample logs).

Always include a revert path for any “demo” configuration.

Next steps

Optional: add a tiny setup.sh that asks “host or sample?” and runs the right docker compose target.

Add CI lint on the parser (flake8) and a LICENSE.

Extend parser to count attempts by IP/user and flag top offenders.

If you’re reviewing this for a junior CSOC/IT role and want a tweak that would read as day-one value for your stack, open an issue or drop me a note.

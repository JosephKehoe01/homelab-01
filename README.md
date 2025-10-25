
# Homelab 01 – Basic Linux Hardening (Ubuntu/Debian)

Use this with either Ubuntu Server or Debian netinst.

## Goal
Reduce attack surface on a fresh Linux server and prove improvement with logs.

## Tools
- SSH (key auth only)
- UFW (firewall)
- fail2ban (rate-limit brute-force)
- journalctl + /var/log/auth.log

See `README.debian.md` for Debian-specific notes.

What I learned

SSH hardening (keys-only, disable root login) + fail2ban cuts down brute-force noise fast.

UFW default-deny is simple, but you must allow SSH before enabling to avoid lockout.

Real evidence matters: logs + a small parser (scripts/parse_authlog.py) tell the story clearly.

Issues faced (and fixes)

Not in sudoers → adduser <me> sudo, log out/in.

Missing SSH server → sudo apt install openssh-server; sudo systemctl enable --now ssh.

UFW inactive → sudo ufw allow 22/tcp then sudo ufw enable.

No auth logs → sudo apt install rsyslog; enable and reboot/start.

Rename host → hostnamectl set-hostname <newname>; update 127.0.1.1 in /etc/hosts.

Next steps

Run Lynis audit; commit report to evidence/.

Add centralised logging (Wazuh or Splunk Free trial) and a short triage note.

Script a one-command bootstrap (install.sh) to reproduce this setup.

Commit message (use for your push)
Home

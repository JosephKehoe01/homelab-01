## Homelab 01 — Debian Hardening (SSH + UFW + fail2ban)

**What I did**
- SSH hardened: keys-only (password auth OFF), `PermitRootLogin no`
- Firewall: UFW default-deny; allow 22/tcp
- Brute-force protection: fail2ban `sshd` jail enabled
- Evidence: parsed `/var/log/auth.log*` into a CSV

**Evidence**
- Screenshots:  
  - `screenshots/ufw-status.png`  
  - `screenshots/fail2ban-status.png`  
  - `screenshots/auth-logs.png`
- CSV: `evidence/auth_failures.csv` (timestamp, host, process, src_ip, message)

**Notes on logs**
- Debian wrote ISO/RFC3339 timestamps (e.g., `2025-10-26T12:23:42+00:00`) and classic `Oct 26 12:23:42` in rotations.  
- `scripts/parse_authlog.py` handles **both** formats and IPv4/IPv6 (`::1`) addresses.

**Issues I hit & fixes**
- User not in `sudo` → added to group, re-logged.
- `ssh` failed to start due to a typo → validated with `sshd -t`, restored default, added drop-in hardening conf.
- UFW inactive → allowed `22/tcp` before enabling.
- No `/var/log/auth.log` at first → installed & enabled `rsyslog`.
- Hostname changed for screenshots; older log rows show previous name (expected).

**Reproduce (quick)**
```bash
sudo apt update && sudo apt install -y openssh-server ufw fail2ban rsyslog git
sudo systemctl enable --now ssh fail2ban rsyslog
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
sudo ufw default deny incoming && sudo ufw default allow outgoing
sudo ufw allow 22/tcp && sudo ufw enable
# generate a couple of failures (optional, for evidence), then lock back down:
# sudo sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config && sudo systemctl restart ssh
# ssh invaliduser@127.0.0.1 || true; ssh "$USER"@127.0.0.1 || true
# sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && sudo systemctl restart ssh
python3 scripts/parse_authlog.py

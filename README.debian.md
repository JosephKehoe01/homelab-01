
# Homelab 01 – Basic Linux Hardening (Debian netinst)

This variant matches the Ubuntu README but uses Debian defaults. Commands are the same, except we rely on `journalctl` and Debian package names.

## Install choices (Debian netinst)
- Tick **SSH server** and **standard system utilities** (no desktop).
- If firmware is requested, allow **non-free firmware** (old Wi‑Fi often needs it).

## First boot
```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y ufw fail2ban git
```

## SSH hardening
```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

## Firewall + fail2ban
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw enable

sudo systemctl enable --now fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl restart fail2ban
```

## Evidence (screenshots)
- `sudo ufw status`
- `sudo fail2ban-client status` and `sudo fail2ban-client status sshd`
- Recent failures:
```bash
sudo journalctl -u ssh --since "24 hours ago" | tail -n 100
sudo zgrep -h "Failed password\|Invalid user" /var/log/auth.log* | tail -n 20
```

## Repo structure
```
homelab-01-basic-hardening/
├─ README.md
├─ README.debian.md
├─ scripts/
│  └─ parse_authlog.py
├─ evidence/
│  └─ auth_failures.csv
└─ screenshots/
   ├─ ufw-status.png
   └─ fail2ban-status.png
```

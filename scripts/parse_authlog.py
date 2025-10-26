#!/usr/bin/env python3
"""
Parse Debian/Ubuntu SSH auth failures into evidence/auth_failures.csv.

- Supports classic syslog timestamps:  "Oct 26 12:23:42 host sshd[1234]: ..."
- Supports ISO/RFC3339 timestamps:     "2025-10-26T12:23:42.387665+00:00 host sshd-session[18107]: ..."
- Scans /var/log/auth.log, .1, and .gz rotations
- Extracts: timestamp, host, process, src_ip (IPv4 preferred, else IPv6), message

Usage:
  python3 scripts/parse_authlog.py
"""

from pathlib import Path
import re, csv, gzip

LOG_DIR = Path("/var/log")
OUT = Path("evidence/auth_failures.csv")
OUT.parent.mkdir(parents=True, exist_ok=True)

# Header matcher: grab ts/host/proc, then everything after the colon as msg
HEADER = re.compile(
    r'^(?P<ts>(?:\w{3}\s+\d{1,2}\s[\d:]{8}|\d{4}-\d{2}-\d{2}T[\d:\.]+[+-]\d{2}:\d{2}))\s+'
    r'(?P<host>\S+)\s+'
    r'(?P<proc>[\w\-\./\[\]]+):\s*'
    r'(?P<msg>.*)$'
)

# IP patterns: prefer IPv4; fall back to IPv6 (requires at least one colon)
IPV4 = re.compile(r'((?:\d{1,3}\.){3}\d{1,3})')
IPV6 = re.compile(r'([A-Fa-f0-9]*:[A-Fa-f0-9:]+)')

# Lines we care about
NEEDLES = ("Failed password", "Invalid user", "authentication failure")

def iter_auth_lines():
    # process plain file first, then rotations (auth.log.1, auth.log.2.gz, …)
    files = sorted(LOG_DIR.glob("auth.log")) + sorted(LOG_DIR.glob("auth.log*"))
    seen = set()
    for p in files:
        if p in seen:  # avoid double
            continue
        seen.add(p)
        if p.suffix == ".gz":
            try:
                with gzip.open(p, "rt", errors="ignore") as f:
                    for ln in f:
                        yield ln.rstrip("\n")
            except Exception:
                continue
        else:
            try:
                with p.open("r", errors="ignore") as f:
                    for ln in f:
                        yield ln.rstrip("\n")
            except Exception:
                continue

def extract_ip(msg: str) -> str:
    m4 = IPV4.search(msg)
    if m4:
        return m4.group(1)
    m6 = IPV6.search(msg)
    return m6.group(1) if m6 else ""

def main():
    rows = []
    for ln in iter_auth_lines():
        if not any(n in ln for n in NEEDLES):
            continue
        m = HEADER.match(ln)
        if not m:
            continue
        g = m.groupdict()
        msg = (g.get("msg") or "").strip()
        ip = extract_ip(msg)
        rows.append({
            "timestamp": g.get("ts", ""),
            "host": g.get("host", ""),
            "process": g.get("proc", ""),
            "src_ip": ip,
            "message": msg
        })

    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["timestamp","host","process","src_ip","message"])
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT}")

if __name__ == "__main__":
    main()




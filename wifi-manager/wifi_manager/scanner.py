"""Discover devices on the local network using a ping sweep plus the OS ARP table.

Only standard-library tools and the operating system's own `ping` / `arp`
commands are used, so nothing is sent beyond ordinary ICMP echo requests on the
user's own subnet.
"""

from __future__ import annotations

import ipaddress
import platform
import re
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

IS_WINDOWS = platform.system() == "Windows"
# Prevent a console window flashing for every ping when run from the GUI.
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

_WIN_ARP_LINE = re.compile(
    r"^\s*(\d{1,3}(?:\.\d{1,3}){3})\s+([0-9a-fA-F]{2}(?:-[0-9a-fA-F]{2}){5})\s+(\w+)"
)
_UNIX_ARP_LINE = re.compile(
    r"\((\d{1,3}(?:\.\d{1,3}){3})\)\s+at\s+([0-9a-fA-F]{1,2}(?::[0-9a-fA-F]{1,2}){5})"
)


@dataclass
class Device:
    ip: str
    mac: str
    name: str = ""
    is_this_pc: bool = False


def normalize_mac(mac: str) -> str:
    parts = re.split(r"[-:]", mac)
    return ":".join(p.zfill(2) for p in parts).upper()


def _is_unicast(ip: str, mac: str) -> bool:
    addr = ipaddress.ip_address(ip)
    if addr.is_multicast or ip.endswith(".255"):
        return False
    return mac not in ("FF:FF:FF:FF:FF:FF", "00:00:00:00:00:00")


def parse_arp_output(text: str) -> list[tuple[str, str]]:
    """Return (ip, mac) pairs from `arp -a` output on Windows, macOS or Linux."""
    pairs: dict[str, str] = {}
    for line in text.splitlines():
        m = _WIN_ARP_LINE.match(line) or _UNIX_ARP_LINE.search(line)
        if not m:
            continue
        ip, mac = m.group(1), normalize_mac(m.group(2))
        if _is_unicast(ip, mac):
            pairs[ip] = mac
    return sorted(pairs.items(), key=lambda p: ipaddress.ip_address(p[0]))


def local_ip() -> str:
    """The IPv4 address this PC uses on its default route (no packet is sent)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


def local_network(prefix: int = 24) -> ipaddress.IPv4Network:
    return ipaddress.ip_network(f"{local_ip()}/{prefix}", strict=False)


def _ping(ip: str) -> None:
    cmd = ["ping", "-n", "1", "-w", "400", ip] if IS_WINDOWS else ["ping", "-c", "1", "-W", "1", ip]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   creationflags=_NO_WINDOW, check=False)


def ping_sweep(network: ipaddress.IPv4Network, workers: int = 64) -> None:
    """Ping every host once so the OS fills its ARP table with live devices."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(_ping, (str(h) for h in network.hosts())))


def read_arp_table() -> list[tuple[str, str]]:
    out = subprocess.run(["arp", "-a"], capture_output=True, text=True,
                         creationflags=_NO_WINDOW, check=False).stdout
    return parse_arp_output(out)


def resolve_name(ip: str) -> str:
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror, OSError):
        return ""


def scan(network: ipaddress.IPv4Network | None = None, sweep: bool = True) -> list[Device]:
    network = network or local_network()
    if sweep:
        ping_sweep(network)
    me = local_ip()
    entries = [(ip, mac) for ip, mac in read_arp_table()
               if ipaddress.ip_address(ip) in network]
    with ThreadPoolExecutor(max_workers=16) as pool:
        names = list(pool.map(resolve_name, (ip for ip, _ in entries)))
    devices = [Device(ip=ip, mac=mac, name=name) for (ip, mac), name in zip(entries, names)]
    # This PC never appears in its own ARP table, so add it explicitly.
    if all(d.ip != me for d in devices):
        devices.insert(0, Device(ip=me, mac="", name=socket.gethostname(), is_this_pc=True))
    return devices

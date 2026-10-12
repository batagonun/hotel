"""Discover devices on the local network using ARP requests, ping and the OS ARP table.

Phones often ignore ping (and sleep their Wi-Fi with the screen off), but every
device must answer an ARP request to stay on the network. On Windows each
address is therefore resolved with the system's SendARP call, the same lookup
Windows does before talking to any neighbour. Ping is still sent so the OS ARP
table fills on other platforms.
"""

from __future__ import annotations

import ipaddress
import platform
import re
import socket
import struct
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


def arp_resolve(ip: str) -> str:
    """Ask Windows to resolve ip with an ARP request; return its MAC or "" if no answer."""
    import ctypes

    buf = (ctypes.c_ubyte * 8)()
    length = ctypes.c_ulong(6)
    dest = struct.unpack("<I", socket.inet_aton(ip))[0]
    if ctypes.windll.iphlpapi.SendARP(dest, 0, ctypes.byref(buf), ctypes.byref(length)) != 0:
        return ""
    return ":".join(f"{b:02X}" for b in buf[: length.value])


def arp_sweep(network: ipaddress.IPv4Network, rounds: int = 2, workers: int = 64) -> dict[str, str]:
    """Resolve every host by ARP; a second round catches phones that were dozing."""
    found: dict[str, str] = {}
    pending = [str(h) for h in network.hosts()]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for _ in range(rounds):
            for ip, mac in zip(pending, pool.map(arp_resolve, pending)):
                if mac and _is_unicast(ip, mac):
                    found[ip] = mac
            pending = [ip for ip in pending if ip not in found]
    return found


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
    found: dict[str, str] = {}
    if sweep:
        if IS_WINDOWS:
            found = arp_sweep(network)
        ping_sweep(network)
    me = local_ip()
    for ip, mac in read_arp_table():
        found.setdefault(ip, mac)
    entries = sorted(((ip, mac) for ip, mac in found.items()
                      if ipaddress.ip_address(ip) in network),
                     key=lambda p: ipaddress.ip_address(p[0]))
    with ThreadPoolExecutor(max_workers=16) as pool:
        names = list(pool.map(resolve_name, (ip for ip, _ in entries)))
    devices = [Device(ip=ip, mac=mac, name=name, is_this_pc=(ip == me))
               for (ip, mac), name in zip(entries, names)]
    # This PC never appears in its own ARP table, so add it explicitly.
    if all(d.ip != me for d in devices):
        devices.insert(0, Device(ip=me, mac="", name=socket.gethostname(), is_this_pc=True))
    return devices

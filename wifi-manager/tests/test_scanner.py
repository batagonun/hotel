import ipaddress
import unittest
from unittest import mock

from wifi_manager import scanner
from wifi_manager.scanner import normalize_mac, parse_arp_output

WINDOWS_ARP = """
Interface: 192.168.1.10 --- 0x7
  Internet Address      Physical Address      Type
  192.168.1.1           a0-b1-c2-d3-e4-f5     dynamic
  192.168.1.23          10-2a-b3-4c-5d-6e     dynamic
  192.168.1.255         ff-ff-ff-ff-ff-ff     static
  224.0.0.22            01-00-5e-00-00-16     static
  239.255.255.250       01-00-5e-7f-ff-fa     static
"""

UNIX_ARP = """
? (192.168.1.1) at a0:b1:c2:d3:e4:f5 [ether] on wlan0
phone.lan (192.168.1.40) at 4:5:6:a:b:c on en0 ifscope [ethernet]
? (192.168.1.50) at <incomplete> on wlan0
"""


class ParseArpTest(unittest.TestCase):
    def test_windows_output_skips_broadcast_and_multicast(self):
        self.assertEqual(parse_arp_output(WINDOWS_ARP), [
            ("192.168.1.1", "A0:B1:C2:D3:E4:F5"),
            ("192.168.1.23", "10:2A:B3:4C:5D:6E"),
        ])

    def test_unix_output_pads_short_octets_and_skips_incomplete(self):
        self.assertEqual(parse_arp_output(UNIX_ARP), [
            ("192.168.1.1", "A0:B1:C2:D3:E4:F5"),
            ("192.168.1.40", "04:05:06:0A:0B:0C"),
        ])

    def test_normalize_mac(self):
        self.assertEqual(normalize_mac("a-b-c-d-e-f"), "0A:0B:0C:0D:0E:0F")


class ArpSweepTest(unittest.TestCase):
    def test_second_round_catches_a_device_that_missed_the_first(self):
        replies = {"192.168.8.1": ["A0:B1:C2:D3:E4:F5"], "192.168.8.5": ["", "11:22:33:44:55:66"]}

        def fake_resolve(ip):
            answers = replies.get(ip)
            return answers.pop(0) if answers else ""

        with mock.patch.object(scanner, "arp_resolve", fake_resolve):
            found = scanner.arp_sweep(ipaddress.ip_network("192.168.8.0/29"))
        self.assertEqual(found, {"192.168.8.1": "A0:B1:C2:D3:E4:F5", "192.168.8.5": "11:22:33:44:55:66"})

    def test_scan_lists_phone_found_only_by_arp(self):
        net = ipaddress.ip_network("192.168.8.0/24")
        with mock.patch.object(scanner, "IS_WINDOWS", True), \
             mock.patch.object(scanner, "arp_sweep", return_value={"192.168.8.23": "AA:BB:CC:DD:EE:FF"}), \
             mock.patch.object(scanner, "ping_sweep"), \
             mock.patch.object(scanner, "read_arp_table", return_value=[("192.168.8.1", "A0:B1:C2:D3:E4:F5")]), \
             mock.patch.object(scanner, "local_ip", return_value="192.168.8.100"), \
             mock.patch.object(scanner, "resolve_name", return_value=""):
            devices = scanner.scan(net)
        self.assertEqual([(d.ip, d.mac, d.is_this_pc) for d in devices], [
            ("192.168.8.100", "", True),
            ("192.168.8.1", "A0:B1:C2:D3:E4:F5", False),
            ("192.168.8.23", "AA:BB:CC:DD:EE:FF", False),
        ])


if __name__ == "__main__":
    unittest.main()

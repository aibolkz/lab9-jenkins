#/usr/bin/env python3


import unittest
from netmiko import ConnectHandler
import re
import subprocess


class TestLab9(unittest.TestCase):

    def setUp(self):
        self.r1 = {
            'device_type': 'cisco_ios',
            'host': '198.51.100.110',
            'username': 'admin',
            'password': 'admin'
        }
        self.r2 = {
            'device_type': 'cisco_ios',
            'host': '198.51.100.120',
            'username': 'admin',
            'password': 'admin'
        }
        self.r3 = {
            'device_type': 'cisco_ios',
            'host': '198.51.100.130',
            'username': 'admin',
            'password': 'admin'
        }


    def test_loopback99_on_r3(self):
        """Checking Loopback99 on R3 — 10.1.3.1/24"""
        conn = ConnectHandler(**self.r3)
        output = conn.send_command("show run interface Loopback99")
        self.assertIn("ip address 10.1.3.1 255.255.255.0", output)
        conn.disconnect()


    def test_single_area_on_r1(self):
        """R1 single OSPF Area"""
        conn = ConnectHandler(**self.r1)
        output = conn.send_command("show run | section ospf")
        area_matches = re.findall(r'area\s+\d+', output)
        self.assertEqual(len(set(area_matches)), 1)
        conn.disconnect()


    def test_ping_r2_to_r5(self):
        """ping from r2 loopback to R5 loopback"""
        result = subprocess.run(["ping", "-c", "3", "10.1.5.1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertIn("0% packet loss", result.stdout)


if __name__ == '__main__':
    unittest.main()

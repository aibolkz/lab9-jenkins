#/usr/bin/env python3


import unittest
from ncclient import manager
from netaddr import IPAddress
import ipaddress
import subprocess


class TestNetmanLab9(unittest.TestCase):

    def setUp(self):
        self.r1_ip = "198.51.100.110"
        self.r3_ip = "198.51.100.130"
        self.username = "admin"
        self.password = "admin"
        self.r2_loopback = "10.1.2.1"
        self.r5_loopback = "10.1.5.1"

    def connect_and_filter(self, host, cli_filter):
        filter_xml = f"""
        <filter>
          <config-format-text-block>
            <text-filter-spec>{cli_filter}</text-filter-spec>
          </config-format-text-block>
        </filter>
        """
        with manager.connect(
            host=host,
            port=22,
            username=self.username,
            password=self.password,
            hostkey_verify=False,
            device_params={'name': 'iosxr'},
            allow_agent=False,
            look_for_keys=False
        ) as conn:
            return str(conn.get_config('running', filter_xml))

    def test_loopback99_on_r3(self):
        """Loopback99 должен быть 10.1.3.1/24 на R3"""
        output = self.connect_and_filter(self.r3_ip, "interface Loopback99")
        self.assertIn("ip address 10.1.3.1 255.255.255.0", output)

    def test_single_ospf_area_on_r1(self):
        """Проверка, что на R1 одна OSPF area"""
        output = self.connect_and_filter(self.r1_ip, "router ospf 1")
        areas = [line for line in output.splitlines() if "area" in line]
        self.assertEqual(len(areas), 1)

    def test_ping_from_r2_to_r5(self):
        """Ping с loopback R2 в loopback R5 должен пройти"""
        result = subprocess.run(
            ["ping", "-c", "3", self.r5_loopback],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertIn("0% packet loss", result.stdout)


if __name__ == '__main__':
    unittest.main()

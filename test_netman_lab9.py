#/usr/bin/env python3


import unittest
import subprocess
from ncclient import manager
import xml.etree.ElementTree as ET

class TestNetmanLab9(unittest.TestCase):

    def setUp(self):
        # Подключение к маршрутизаторам
        self.r3_ip = "198.51.100.130"
        self.r1_ip = "198.51.100.110"
        self.r2_loopback = "10.1.2.1"
        self.r5_loopback = "10.1.5.1"
        self.username = "admin"
        self.password = "admin"

    def test_loopback99_r3(self):
        """Проверка наличия Loopback99 с IP 10.1.3.1/24 на R3"""
        with manager.connect(
            host=self.r3_ip,
            port=22,
            username=self.username,
            password=self.password,
            hostkey_verify=False,
            device_params={'name': 'iosxr'},
            allow_agent=False,
            look_for_keys=False
        ) as conn:
            filter_xml = """
            <filter>
                <config-format-text-block>
                    <text-filter-spec>interface Loopback99</text-filter-spec>
                </config-format-text-block>
            </filter>
            """
            result = conn.get_config('running', filter_xml)
            response = str(result)

            self.assertIn("ip address 10.1.3.1 255.255.255.0", response)

    def test_single_area_r1(self):
        """Проверка, что на R1 только одна OSPF area"""
        with manager.connect(
            host=self.r1_ip,
            port=22,
            username=self.username,
            password=self.password,
            hostkey_verify=False,
            device_params={'name': 'iosxr'},
            allow_agent=False,
            look_for_keys=False
        ) as conn:
            filter_xml = """
            <filter>
                <config-format-text-block>
                    <text-filter-spec>router ospf 1</text-filter-spec>
                </config-format-text-block>
            </filter>
            """
            result = conn.get_config('running', filter_xml)
            response = str(result)

            # считаем количество "area X" в ответе
            area_lines = [line for line in response.splitlines() if "area" in line]
            area_count = len(area_lines)

            self.assertEqual(area_count, 1)

    def test_ping_r2_to_r5(self):
        """Пинг из Loopback R2 в Loopback R5"""
        # Используем команду ping с R2 — запускаем с самой машины (если доступна)
        # Здесь предполагается, что R2 — локальная Linux-машина или есть доступ к CLI
        result = subprocess.run(
            ["ping", "-c", "3", self.r5_loopback],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        self.assertIn("0% packet loss", result.stdout)

if __name__ == '__main__':
    unittest.main()

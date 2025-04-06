#/usr/bin/env python3


import unittest
from ncclient import manager
import subprocess


class TestNetmanLab9(unittest.TestCase):

    def setUp(self):
        self.r1_ip = "198.51.100.110"
        self.r3_ip = "198.51.100.130"
        self.username = "admin"
        self.password = "admin"
        self.r5_loopback = "10.1.5.1"

    def send_rpc_cli(self, host, cli_command):
        """Отправка CLI-команды через NETCONF <cli><cmd>"""
        cli_rpc = f"""
        <rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
          <cli>
            <cmd>{cli_command}</cmd>
          </cli>
        </rpc>
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
            return str(conn.dispatch(cli_rpc))

    def test_loopback99_on_r3(self):
        """Loopback99 должен быть 10.1.3.1/24 на R3"""
        output = self.send_rpc_cli(self.r3_ip, "show run interface Loopback99")
        self.assertIn("ip address 10.1.3.1 255.255.255.0", output)

    def test_single_ospf_area_on_r1(self):
        """Проверка, что на R1 одна OSPF area"""
        output = self.send_rpc_cli(self.r1_ip, "show run | section ospf")
        area_count = output.count("area")
        self.assertEqual(area_count, 1)

    def test_ping_r2_to_r5(self):
        """Ping от Loopback R2 до Loopback R5"""
        result = subprocess.run(
            ["ping", "-c", "3", self.r5_loopback],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.assertIn("0% packet loss", result.stdout)


if __name__ == '__main__':
    unittest.main()

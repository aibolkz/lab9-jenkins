#/usr/bin/env python3
import csv
import ipaddress
from ncclient import manager
from prettytable import PrettyTable
import time



def netconf_config(file):
    router_ips = {
        "R1": "198.51.100.110",
        "R2": "198.51.100.120",
        "R3": "198.51.100.130",
        "R4": "198.51.100.140",
        "R5": "198.51.100.150"
    }


    
    USERNAME = "admin"
    PASSWORD = "admin"
    results = []



    with open(file, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        reader.fieldnames = [field.strip() for field in reader.fieldnames]

        for row in reader:
            router = row.get("Router").strip()
            hostname = row.get("Hostname").strip()
            loopback_ip = row.get("Loopback 99 IP").strip()
            ospf_area = row.get("OSPF area").strip()
            ospf_network = row.get("OSPF Network to advertise").strip()
            mgmt_ip = router_ips[router]

            
            
            
            #status = "broken"

            try:
                ip_iface = ipaddress.ip_interface(loopback_ip)
                loopback_addr = str(ip_iface.ip)
                loopback_mask = str(ip_iface.network.netmask)


            except Exception:
                loopback_addr = loopback_ip
                loopback_mask = "255.255.255.0"



            try:
                if "/" in ospf_network:
                    net = ipaddress.ip_network(ospf_network, strict=False)
                    network_addr = str(net.network_address)
                    wildcard_mask = str(net.hostmask)
                elif " " in ospf_network:
                    parts = ospf_network.split()
                    network_addr = parts[0]
                    wildcard_mask = parts[1] if len(parts) > 1 else "0.0.0.0"
                else:
                    network_addr = ospf_network
                    wildcard_mask = "0.0.0.255"
            
            
            except Exception:
                network_addr = ospf_network
                wildcard_mask = "0.0.0.255"

           
           
            try:
                with manager.connect(
                    host=router_ips[router],
                    port=22,
                    username=USERNAME,
                    password=PASSWORD,
                    hostkey_verify=False,
                    allow_agent=False,
                    look_for_keys=False,
                    timeout=5
                ) as m:
                    config_payload = f"""
                    <config>
                      <cli-config-data>
                        <cmd>hostname {hostname}</cmd>
                        <cmd>interface Loopback99</cmd>
                        <cmd>ip address {loopback_addr} {loopback_mask}</cmd>
                        <cmd>exit</cmd>
                        <cmd>router ospf 1</cmd>
                        <cmd>network {mgmt_ip} {wildcard_mask} area {ospf_area}</cmd>
                        <cmd>network {network_addr} {wildcard_mask} area {ospf_area}</cmd>
                      </cli-config-data>
                    </config>
                    """
                    m.dispatch(config_payload)

            
            
            except:
                pass

            results.append([router, hostname, loopback_ip, ospf_area, ospf_network])

    #wait until ospf makes neighborships
    time.sleep(30)
    table = PrettyTable(["Router", "Hostname", "Loopback 99", "OSPF Area", "OSPF Network"])
    for row in results:
        table.add_row(row)

    print("\n Output:")
    print(table)



if __name__ == "__main__":
    netconf_config("lab9-obj2-conf.csv")

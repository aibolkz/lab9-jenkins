from __future__ import print_function

try:
    from ncclient import manager
    from prettytable import PrettyTable
    from netaddr import IPAddress
    import pandas as pd
    import ipaddress
    import os
    import sys
except Exception:
    print("Install all the necessary modules")
    sys.exit()

if __name__ == "__main__":
    table = PrettyTable(['Router', 'Hostname', 'Loopback 99 IP', 'OSPF area', 'Advertised OSPF Networks'])
    file = 'info.csv'

    if not os.path.exists(file):
        print(f"File {file} not found, exiting")
        sys.exit()
    if os.stat(file).st_size == 0:
        print(f"File {file} is empty, exiting")
        sys.exit()

    df = pd.read_csv(file)
    routers = df['Router'].to_list()
    mgmt_ip = df['Mgmt IP'].to_list()
    uname = df['Username'].to_list()
    pwd = df['Password'].to_list()
    hostname_list = df['Hostname'].to_list()
    lo_name = df['Loopback Name'].to_list()
    lo_ip = df['Loopback IP'].to_list()
    mask = df['Loopback Subnet'].to_list()
    wildcard = df['Wildcard'].to_list()
    networks = df['Network'].to_list()
    area = df['OSPF Area'].to_list()

    cfg_template = '''
    <config>
      <cli-config-data>
        <cmd>hostname {}</cmd>
        <cmd>int {}</cmd>
        <cmd>ip address {} {}</cmd>
        <cmd>router ospf 1</cmd>
        <cmd>network {} {} area {}</cmd>
        <cmd>network 198.51.100.0 0.0.0.255 area 0</cmd>
      </cli-config-data>
    </config>
    '''

    for i in range(5):
        print(f"Connecting to {routers[i]} at {mgmt_ip[i]} with user {uname[i]}")
        conn = manager.connect(
            host=mgmt_ip[i],
            port=22,
            username=uname[i],
            password=pwd[i],
            hostkey_verify=False,
            device_params={'name': 'iosxr'},
            allow_agent=False,
            look_for_keys=False
        )
        print(f"Sending config to {routers[i]}...")
        cfg = cfg_template.format(hostname_list[i], lo_name[i], lo_ip[i], mask[i], networks[i], wildcard[i], area[i])
        conn.edit_config(target='running', config=cfg)

    print("\n------------------Configs to all routers sent------------------\n")

    fetch_info = '''
    <filter>
      <config-format-text-block>
        <text-filter-spec>{}</text-filter-spec>
      </config-format-text-block>
    </filter>
    '''

    for i in range(5):
        print(f"Connecting to {routers[i]} at {mgmt_ip[i]} with user {uname[i]}")
        conn = manager.connect(
            host=mgmt_ip[i],
            port=22,
            username=uname[i],
            password=pwd[i],
            hostkey_verify=False,
            device_params={'name': 'iosxr'},
            allow_agent=False,
            look_for_keys=False
        )

        hostname_cmd = fetch_info.format('| i hostname')
        output1 = conn.get_config('running', hostname_cmd)
        hostname = str(output1).split()[6]

        lo_cmd = fetch_info.format('int Loopback99')
        output2 = conn.get_config('running', lo_cmd)
        split2 = str(output2).split()
        lo_ip_mask = f"{split2[9]}/{IPAddress(split2[10]).netmask_bits()}"

        ospf_cmd = fetch_info.format('| s ospf')
        output3 = conn.get_config('running', ospf_cmd)
        split3 = str(output3).split()
        lo_ip_prefix = ipaddress.ip_network(f"{split3[9]}/{split3[10]}", strict=False).prefixlen
        mgm_ip_prefix = ipaddress.ip_network(f"{split3[14]}/{split3[15]}", strict=False).prefixlen
        ospf_area = split3[12]
        ospf_networks = f"{split3[9]}/{lo_ip_prefix}, {split3[14]}/{mgm_ip_prefix}"

        table.add_row([routers[i], hostname, lo_ip_mask, ospf_area, ospf_networks])

    print("\n------------------Displaying the fetched information------------------\n")
    print(table)

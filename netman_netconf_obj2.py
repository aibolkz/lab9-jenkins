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
    print('Install all the necessary modules')
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

    read_file = pd.read_csv(file)
    routers = read_file['Router'].to_list()
    mgmt_ip = read_file['Mgmt IP'].to_list()
    uname = read_file['Username'].to_list()
    pwd = read_file['Password'].to_list()
    host = read_file['Hostname'].to_list()
    lo_name = read_file['Loopback Name'].to_list()
    lo_ip = read_file['Loopback IP'].to_list()
    mask = read_file['Loopback Subnet'].to_list()
    wildcard = read_file['Wildcard'].to_list()
    networks = read_file['Network'].to_list()
    area = read_file['OSPF Area'].to_list()

    cfg = '''
    <config>
    <cli-config-data>
    <cmd> hostname %s </cmd>
    <cmd> int %s </cmd>
    <cmd> ip address %s %s </cmd>
    <cmd> router ospf 1 </cmd>
    <cmd> network %s %s area %s </cmd>
    <cmd> network 198.51.100.0 0.0.0.255 area 0 </cmd>
    </cli-config-data>
    </config>
    '''

    for i in range(0, 5):
        print(f"Connecting to {routers[i]} at {mgmt_ip[i]} with user {uname[i]}")
        connection = manager.connect(
            host=mgmt_ip[i],
            port=22,
            username=uname[i],
            password=pwd[i],
            hostkey_verify=False,
            device_params={'name': 'iosxr'},
            allow_agent=False,
            look_for_keys=False
        )
        print(f'Logging into router {routers[i]} and sending configurations')
        cfg1 = cfg % (host[i], lo_name[i], lo_ip[i], mask[i], networks[i], wildcard[i], area[i])
        connection.edit_config(target='running', config=cfg1)

    print('\n------------------Configs to all routers is sent------------------\n')

    fetch_info = '''
    <filter>
    <config-format-text-block>
    <text-filter-spec> %s </text-filter-spec>
    </config-format-text-block>
    </filter>
    '''

    for i in range(0, 5):
        print(f"Connecting to {routers[i]} at {mgmt_ip[i]} for fetching info")
        connection = manager.connect(
            host=mgmt_ip[i],
            port=22,
            username='admin',
            password='admin',
            hostkey_verify=False,
            device_params={'name': 'iosxr'},
            allow_agent=False,
            look_for_keys=False
        )
        print(f'Pulling information from router {routers[i]} to display')

        fetch_hostname = fetch_info % '| i hostname'
        output1 = connection.get_config('running', fetch_hostname)
        split1 = str(output1).split()
        hostname = split1[6]

        fetch_lo_info = fetch_info % 'int Loopback99'
        output2 = connection.get_config('running', fetch_lo_info)
        split2 = str(output2).split()
        lo_ip_mask = split2[9] + '/' + str(IPAddress(split2[10]).netmask_bits())

        fetch_ospf_info = fetch_info % '| s ospf'
        output3 = connection.get_config('running', fetch_ospf_info)
        split3 = str(output3).split()
        lo_ip_prefix = str(ipaddress.ip_network(split3[9] + '/' + split3[10], strict=False).prefixlen)
        mgmt_ip_prefix = str(ipaddress.ip_network(split3[14] + '/' + split3[15], strict=False).prefixlen)
        ospf_area = split3[12]
        ospf_networks = f"{split3[9]}/{lo_ip_prefix}, {split3[14]}/{mgmt_ip_prefix}"

        table.add_row((routers[i], hostname, lo_ip_mask, ospf_area, ospf_networks))

    print('\n------------------Displaying the fetched information------------------\n')
    print(table)

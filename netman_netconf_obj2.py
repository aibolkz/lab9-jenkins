from __future__ import print_function

try:
    from ncclient import manager
    import pandas as pd
    import os
    import sys
except Exception:
    print('Install all the necessary modules')
    sys.exit()

if __name__ == "__main__":
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
    hostname = read_file['Hostname'].to_list()
    loop_name = read_file['Loopback Name'].to_list()
    loop_ip = read_file['Loopback IP'].to_list()
    mask = read_file['Loopback Subnet'].to_list()
    ospf_area = read_file['OSPF Area'].to_list()
    network = read_file['Network'].to_list()
    wildcard = read_file['Wildcard'].to_list()

    cfg_template = """
    <config>
      <cli-config-data>
        <cmd>hostname {}</cmd>
        <cmd>interface {}</cmd>
        <cmd>ip address {} {}</cmd>
        <cmd>router ospf 1</cmd>
        <cmd>network {} {} area {}</cmd>
        <cmd>network 198.51.100.0 0.0.0.255 area 0</cmd>
      </cli-config-data>
    </config>
    """

    for i in range(len(routers)):
        print(f"Connecting to {routers[i]} at {mgmt_ip[i]} with user {uname[i]}")
        try:
            conn = manager.connect(
                host=mgmt_ip[i],
                port=22,
                username=uname[i],
                password=pwd[i],
                hostkey_verify=False,
                device_params={'name': 'iosxr'},
                allow_agent=False,
                look_for_keys=False,
                timeout=30
            )

            config_payload = cfg_template.format(
                hostname[i], loop_name[i], loop_ip[i], mask[i],
                network[i], wildcard[i], ospf_area[i]
            )

            result = conn.edit_config(target='running', config=config_payload)
            print(f"Config pushed to {routers[i]} successfully.")
            print(result)

        except Exception as e:
            print(f"Failed to configure {routers[i]} at {mgmt_ip[i]}: {e}")

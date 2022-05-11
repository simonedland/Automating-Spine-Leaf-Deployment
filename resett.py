from typing import NoReturn
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get
from tqdm import tqdm
import time

def resettHostName(node):
    node.run(task=netmiko_send_config, config_commands=[f"hostname {str(node.host).split('.')[0]}", "ip domain-name simon"])


def resetter(node):
    pbar = tqdm(total=2)
    pbar.set_description(f"gathering info on {node.host.hostname}")

    interfacesNetmiko = node.run(task = netmiko_send_command, command_string = "show ip int", use_textfsm = True).result
    pbar.colour="yellow"
    pbar.update()
    time.sleep(0.2)

    for interface in interfacesNetmiko:
        try:
            if  "10.100.0." in interface["ipaddr"][0]:
                sshInterface = interface["intf"]
        except:
            pass


    interfacesNapalm = node.run(task=napalm_get, getters=["interfaces"]).result
    pbar.colour="green"
    pbar.update()
    time.sleep(0.5)
    pbar.leave = False
    time.sleep(0.5)

    pbar = tqdm(total=(2))


    #can make this part way faster by making a single command list and then running it all at once
    node.run(task=netmiko_send_config, config_commands=["ip routing","ip route 0.0.0.0 0.0.0.0 10.100.0.100"])

    pbar.set_description(f"did basic router configgs")
    pbar.colour="yellow"
    pbar.update()

    #this needs some work
    commandList = []
    for i in interfacesNapalm["interfaces"]:
        if i != sshInterface:
            commandList.extend(["interface " + i , "no shutdown", "no port channel", "no channel-group", "switchport", "no ip ospf 1 area 0", "no description", "switchport mode access", "switchport access vlan 1"])
        else:
            commandList.extend(["interface " + i , "no switchport", "no ip ospf 1 area 0", "description ssh"])



    node.run(task=netmiko_send_config, config_commands=commandList)

    time.sleep(0.5)
    pbar.colour="green"
    pbar.update()
    pbar.leave = False
    time.sleep(0.5)

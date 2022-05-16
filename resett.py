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

    pbar1 = tqdm(total=(2))
    pbar1.set_description(f"doing basic router configgs")

    #can make this part way faster by making a single command list and then running it all at once
    node.run(task=netmiko_send_config, config_commands=["ip routing","ip route 192.168.1.0 255.255.255.0 10.100.0.100","no ip route 0.0.0.0 0.0.0.0 10.100.0.100"])

    pbar1.set_description(f"sending all interface reset commands")
    pbar1.colour="yellow"
    pbar1.update()

    #this needs some work
    commandList = []
    #print(interfacesNapalm["interfaces"])
    for i in interfacesNapalm["interfaces"]:
        if i != sshInterface:
            if "Vlan" in i:
                commandList.extend(["interface " + i , f"no ip add" ,"no shutdown", "no port channel", "no channel-group",f"no standby 1 ip ", f"no standby 1 preempt", f"no standby 1 priority", "no ip ospf 1 area 0", "no description"])
            commandList.extend(["interface " + i , "no shutdown", "no port channel", "no channel-group", "switchport", "no ip ospf 1 area 0", "no description", "switchport mode access", "switchport access vlan 1"])
        else:
            commandList.extend(["interface " + i , "no switchport", "description ssh"])



    node.run(task=netmiko_send_config, config_commands=commandList)

    pbar1.set_description(f"done resetting interfaces")
    pbar1.colour="green"
    pbar1.update()


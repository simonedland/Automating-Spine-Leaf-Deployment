from typing import NoReturn
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get
from tqdm import tqdm
import time


def resetter(node):
    pbar = tqdm(total=1)
    pbar.set_description(f"{node.host.hostname}")

    interfacesNetmiko = node.run(task = netmiko_send_command, command_string = "show ip int", use_textfsm = True).result

    for interface in interfacesNetmiko:
        print(interface)


    interfacesNapalm = node.run(task=napalm_get, getters=["interfaces"]).result
    pbar.update()
    time.sleep(0.2)
    pbar.close()
    
    
    print(interfacesNapalm["interfaces"].keys())
    for x in interfacesNapalm["interfaces"].keys():
        print(interfacesNapalm["interfaces"][x])
        print(interfacesNapalm["interfaces"][x]["description"])
        print(interfacesNapalm["interfaces"][x]["mac_address"])
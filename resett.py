from typing import NoReturn
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get
from tqdm import tqdm
import time

def resettHostName(node): #this is a bit of a hack, but it works
    node.run(task=netmiko_send_config, config_commands=[f"hostname {str(node.host).split('.')[0]}", "ip domain-name simon"])


def resetter(node): #main function of this script
    pbar = tqdm(total=2) #progress bar
    pbar.set_description(f"gathering info on {node.host.hostname}") #writes to the progress bar
    interfacesNetmiko = node.run(task = netmiko_send_command, command_string = "show ip int", use_textfsm = True).result #this is the netmiko interface information
    pbar.colour="yellow"
    pbar.update()

    for interface in interfacesNetmiko: #for every interface in the interface information
        try:
            if  "10.100.0." in interface["ipaddr"][0]: #if the interface is connected to the ssh server
                sshInterface = interface["intf"] #this is the interface that is connected to the ssh server
        except:
            pass


    interfacesNapalm = node.run(task=napalm_get, getters=["interfaces"]).result #this is the napalm interface information
    pbar.colour="green"
    pbar.update()

    pbar1 = tqdm(total=(2))
    pbar1.set_description(f"doing basic router configgs")

    #can make this part way faster by making a single command list and then running it all at once
    node.run(task=netmiko_send_config, config_commands=["ip routing","ip route 192.168.1.51 255.255.255.255 10.100.0.100", "no ip route 0.0.0.0 0.0.0.0 192.168.1.1", "no access-list 1","no ip nat inside source list 1 interface g0/2 overload"]) #this is the basic config for the router to connect to the ssh server

    pbar1.set_description(f"sending all interface reset commands")
    pbar1.colour="yellow"
    pbar1.update()

    #!this needs some work due to not beeing modular
    commandList = [f"no track 1","no track 2", "no track 3", "no track 4", "no router eigrp 1",f"no router ospf 1"] #this is the list of commands to run
    for i in interfacesNapalm["interfaces"]: #for every interface in the napalm interface information
        if i != sshInterface:
            if "Vlan" in i: #if the interface is a vlan
                commandList.extend(["interface " + i , f"no ip add" ,"no shutdown", f"no standby 1 ip ", f"no standby 1 preempt", f"no standby 1 priority", f"no standby 1 track 1", "no description"])
            
            elif "Tunnel" in i: #if the interface is a loopback
                commandList.extend(["interface " + i , f"no ip add" , f"no tunnel source", f"no destination", f"exit", f"no int {i}"])

            elif "Loop" in i:#if the interface is a loopback
                commandList.extend(["interface " + i , f"no ip add" ,"no shutdown"])
            
            else: #if the interface is a normal interface
                commandList.extend(["interface " + i , "no shutdown", "no channel-group", "switchport", "no description", "switchport mode access", "switchport access vlan 1","no ip nat outside","no ip nat inside", "no ip address"])
        
        else: #if the interface is connected to the ssh server
            commandList.extend(["interface " + i , "no switchport", "description ssh"])

    node.run(task=netmiko_send_config, config_commands=commandList) #this is the final command list to run

    pbar1.set_description(f"done resetting interfaces")
    pbar1.colour="green"
    pbar1.update()


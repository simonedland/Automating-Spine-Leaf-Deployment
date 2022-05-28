from typing import NoReturn
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get
from tqdm import tqdm
from nornir import InitNornir
from nornir.core.filter import F
from Subbnetter import subbnetter
import time

def resettHostName(node): #this is a bit of a hack, but it works
    StartTime = time.time()
    node.run(task=netmiko_send_config, config_commands=[f"hostname {str(node.host).split('.')[0]}", "ip domain-name simon"])
    EndTime = time.time()
    return 2, EndTime-StartTime


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

    nr = InitNornir(config_file="config.yaml") #this is the nornir object
    Pairs = int(len(nr.inventory.children_of_group("leaf"))/2) #this is the number of leafs
    DHCP_Pools = (subbnetter(nettwork=f"192.168.2.0",nettworkReq=[{"numberOfSubbnets":Pairs, "requiredHosts":255},]))


    interfacesNapalm = node.run(task=napalm_get, getters=["interfaces"]).result #this is the napalm interface information


    #?COPPY PASTE FROM DHCP POOL GENERATOR

    node.host["cdp"] = node.run(task=netmiko_send_command, command_string=("sh cdp nei de")).result #this is the interface information
    node.host["run"] = node.run(task=netmiko_send_command, command_string=("sh run"), enable=True).result #this is the running config
    hostnames = [i for i in range(len(node.host["cdp"])) if node.host["cdp"].startswith("Device ID:", i)] #finds the location of the device id
    interfaces = [i for i in range(len(node.host["cdp"])) if node.host["cdp"].startswith("Interface:", i)] #finds the location of the interface
    cdpNeigbourDirections=[]
    for x in range(len(hostnames)):
        hostname = (node.host["cdp"][hostnames[x]+11:hostnames[x]+24].split("\n")[0].split(".")[0]) #this is the hostname of the neigbour
        interface = (node.host["cdp"][interfaces[x]+11:interfaces[x]+30].split("\n")[0].split(".")[0].split(",")[0]) #this is the interface that the neigbour is connected to
        if hostname != "Switch": #this is to make sure that the hostname is not just a switch
            cdpNeigbourDirections.append({"name":hostname, "interface":interface})
    try:
        switchpair=node.host['switchpair']-1
        locationOfQuote=node.host["run"].find(f"hostname leaf")
        LeafNr=int(node.host["run"][locationOfQuote+13:locationOfQuote+15].replace(" ","").replace("\n",""))
    except:
        switchpair=0
        LeafNr=0

    for x in cdpNeigbourDirections: #for every neigbour in the cdp neigbour list
        if "leaf" in x["name"]: #if the neigbour is a leaf
            try: #try to search if the number is over 9
                connectedLeafNr=(int(x["name"][len(x["name"])-2:len(x["name"])])) #probably not the best way to do this
            except: #if not over 9
                connectedLeafNr=(int(x["name"][len(x["name"])-1:len(x["name"])]))

    if connectedLeafNr>LeafNr: #if the connected leaf is greater than the current leaf
        TakeUpperIpRange=True #standby priority

    else: #if the connected leaf is less than the current leaf
        TakeUpperIpRange=False #standby priority
    if TakeUpperIpRange:
        excludLow=f"{str(DHCP_Pools[switchpair]['subbnetID']).split('.')[0]}.{str(DHCP_Pools[switchpair]['subbnetID']).split('.')[1]}.{str(DHCP_Pools[switchpair]['subbnetID']).split('.')[2]}.128"
        excludHigh=f"{str(DHCP_Pools[switchpair]['subbnetID']).split('.')[0]}.{str(DHCP_Pools[switchpair]['subbnetID']).split('.')[1]}.{str(DHCP_Pools[switchpair]['subbnetID']).split('.')[2]}.250"
    else:
        excludLow=f"{str(DHCP_Pools[switchpair]['subbnetID']).split('.')[0]}.{str(DHCP_Pools[switchpair]['subbnetID']).split('.')[1]}.{str(DHCP_Pools[switchpair]['subbnetID']).split('.')[2]}.10"
        excludHigh=f"{str(DHCP_Pools[switchpair]['subbnetID']).split('.')[0]}.{str(DHCP_Pools[switchpair]['subbnetID']).split('.')[1]}.{str(DHCP_Pools[switchpair]['subbnetID']).split('.')[2]}.127"
    
    #?END OF COPPYPASTE


    pbar.colour="green"
    pbar.update()

    pbar1 = tqdm(total=(2))
    pbar1.set_description(f"doing basic router configgs")

    node.run(task=netmiko_send_config, config_commands=["ip routing",
                                                        "ip route 192.168.1.51 255.255.255.255 10.100.0.100",
                                                        "no ip route 192.168.1.0 255.255.255.0 10.100.0.100", 
                                                        "no access-list 1",
                                                        "no ip nat inside source list 1 interface g0/2 overload"
                                                        "exit",
                                                        "no ip dhcp pool Pool",
                                                        f"no ip dhcp excluded-address {excludLow} {excludHigh}"]) #this is the basic config for the router to connect to the ssh server

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


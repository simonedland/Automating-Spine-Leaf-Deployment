from nornir_netmiko.tasks import netmiko_send_config, netmiko_send_command
import time
from nornir_utils.plugins.functions import print_result


def AddDHCPPools(node, ipconfigs, gateway="first"):
    StartTime=time.time()

    """makes the command list of adding the dhcp pools with netmiko
    normaly used with my subbnetter script
    requires a list of dictionaries with the keys: subbnetID, broadcast and mask
    this also points the dns to 8.8.8.8
    the gateway is placed in the first avadable adress this can be spesified by setting the gateway="last" when caling
    """
    
    #!CISCO does not support DHCP FAILOVER BUT WE CAN THEN JUST SPLITT THE DHCP POOLS INTO 2
    #!this should be done by excluding half of the subnets from the pool

    GatherStartTime=time.time()
    node.host["cdp"] = node.run(task=netmiko_send_command, command_string=("sh cdp nei de")).result #this is the interface information
    node.host["run"] = node.run(task=netmiko_send_command, command_string=("sh run"), enable=True).result #this is the running config
    GatherEndTime=time.time()
    hostnames = [i for i in range(len(node.host["cdp"])) if node.host["cdp"].startswith("Device ID:", i)] #finds the location of the device id
    interfaces = [i for i in range(len(node.host["cdp"])) if node.host["cdp"].startswith("Interface:", i)] #finds the location of the interface
    cdpNeigbourDirections=[]
    for x in range(len(hostnames)):
        hostname = (node.host["cdp"][hostnames[x]+11:hostnames[x]+24].split("\n")[0].split(".")[0]) #this is the hostname of the neigbour
        interface = (node.host["cdp"][interfaces[x]+11:interfaces[x]+30].split("\n")[0].split(".")[0].split(",")[0]) #this is the interface that the neigbour is connected to
        if hostname != "Switch": #this is to make sure that the hostname is not just a switch
            cdpNeigbourDirections.append({"name":hostname, "interface":interface})
    switchpair=node.host['switchpair']-1
    locationOfQuote=node.host["run"].find(f"hostname leaf")
    LeafNr=int(node.host["run"][locationOfQuote+13:locationOfQuote+15].replace(" ","").replace("\n",""))

    for x in cdpNeigbourDirections: #for every neigbour in the cdp neigbour list
        if "leaf" in x["name"]: #if the neigbour is a leaf
            try: #try to search if the number is over 9
                connectedLeafNr=(int(x["name"][len(x["name"])-2:len(x["name"])])) #probably not the best way to do this
            except: #if not over 9
                connectedLeafNr=(int(x["name"][len(x["name"])-1:len(x["name"])]))

    if connectedLeafNr>LeafNr: #if the connected leaf is greater than the current leaf
        TakeUpperIpRange=True #standby priority

    else: #if the connected leaf is less than the current leaf
        TakeUpperIpRange=False

    counter=0
    commandlist=[]
    
    if gateway =="first":
        gateway=f"{str(ipconfigs[switchpair]['subbnetID']).split('.')[0]}.{str(ipconfigs[switchpair]['subbnetID']).split('.')[1]}.{str(ipconfigs[switchpair]['subbnetID']).split('.')[2]}.{int(str(ipconfigs[switchpair]['subbnetID']).split('.')[3])+1}"
    elif gateway =="last":
        gateway=f"{str(ipconfigs[switchpair]['broadcast']).split('.')[0]}.{str(ipconfigs[switchpair]['broadcast']).split('.')[1]}.{str(ipconfigs[switchpair]['broadcast']).split('.')[2]}.{int(str(ipconfigs[switchpair]['broadcast']).split('.')[3])-1}"
    else:
        gateway=f"{str(ipconfigs[switchpair]['subbnetID']).split('.')[0]}.{str(ipconfigs[switchpair]['subbnetID']).split('.')[1]}.{str(ipconfigs[switchpair]['subbnetID']).split('.')[2]}.{int(str(ipconfigs[switchpair]['subbnetID']).split('.')[3])+1}"

    if TakeUpperIpRange:
        excludLow=f"{str(ipconfigs[switchpair]['subbnetID']).split('.')[0]}.{str(ipconfigs[switchpair]['subbnetID']).split('.')[1]}.{str(ipconfigs[switchpair]['subbnetID']).split('.')[2]}.128"
        excludHigh=f"{str(ipconfigs[switchpair]['subbnetID']).split('.')[0]}.{str(ipconfigs[switchpair]['subbnetID']).split('.')[1]}.{str(ipconfigs[switchpair]['subbnetID']).split('.')[2]}.250"
    else:
        excludLow=f"{str(ipconfigs[switchpair]['subbnetID']).split('.')[0]}.{str(ipconfigs[switchpair]['subbnetID']).split('.')[1]}.{str(ipconfigs[switchpair]['subbnetID']).split('.')[2]}.10"
        excludHigh=f"{str(ipconfigs[switchpair]['subbnetID']).split('.')[0]}.{str(ipconfigs[switchpair]['subbnetID']).split('.')[1]}.{str(ipconfigs[switchpair]['subbnetID']).split('.')[2]}.127"
    
        
    commandlist.append(f"ip dhcp excluded-address {excludLow} {excludHigh}")
    commandlist.append(f"ip dhcp pool Pool")
    commandlist.append(f"network {ipconfigs[switchpair]['subbnetID']} {ipconfigs[switchpair]['mask']}")
    commandlist.append(f"dns-server 8.8.8.8")
    commandlist.append(f"default-router {gateway}")
    commandlist.append(f"exit")

    CommandStartTime=time.time()
    node.run(task=netmiko_send_config, config_commands=commandlist)
    CommandEndTime=time.time()

    EndTime=time.time()

    return len(commandlist)+2, EndTime-StartTime , GatherEndTime-GatherStartTime, CommandEndTime-CommandStartTime
#TODO:
#!find out what vlan to use (security)
#implement priority decrementing based on interfaces
#use CDP to find out what interfaces are connected to what
#ignore STP due to the switches only beeing connected to one another unless the server is switched this means that i can use portfast
#trunking the interfaces
#?some of the information might be usefull to save for the tunneling but then again i want to make it modular to prevent having to change the code in difrent places then where the issue is

from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from Subbnetter import subbnetter

def hsrpPair(node):
    subbnetList=[]
    subbnetList.append(subbnetter(nettwork=f"172.27.0.0",
        nettworkReq=[
        {"numberOfSubbnets":10, "requiredHosts":255},
        ])) #makes 1 subbnets with 255 hosts each

    #constructs the interface information and running config information
    node.host["cdp"] = node.run(task=netmiko_send_command, command_string=("sh cdp nei de")).result
    node.host["run"] = node.run(task=netmiko_send_command, command_string=("sh run"), enable=True).result

    hostnames = [i for i in range(len(node.host["cdp"])) if node.host["cdp"].startswith("Device ID:", i)] #finds the location of the device id
    interfaces = [i for i in range(len(node.host["cdp"])) if node.host["cdp"].startswith("Interface:", i)] #finds the location of the interface

    cdpNeigbourDirections=[]
    for x in range(len(hostnames)):
        hostname = (node.host["cdp"][hostnames[x]+11:hostnames[x]+24].split("\n")[0].split(".")[0]) #this is the hostname of the neigbour
        interface = (node.host["cdp"][interfaces[x]+11:interfaces[x]+30].split("\n")[0].split(".")[0].split(",")[0]) #this is the interface that the neigbour is connected to
        if hostname != "Switch":
            cdpNeigbourDirections.append({"name":hostname, "interface":interface})


    #check if self is in a switchpair and if so what is the other side
    try:
        switchpair=node.host['switchpair']
        spine=False
    except:
        spine=True

    if spine==False:

        #finds out what switchnumber the node is (code from subbnetter)
        locationOfQuote=node.host["run"].find(f"hostname leaf")
        LeafNr=int(node.host["run"][locationOfQuote+13:locationOfQuote+15].replace(" ","").replace("\n",""))
        
        #a loop to find leafs in the cdp neigbour list
        for x in cdpNeigbourDirections:
            if "leaf" in x["name"]:
                try:
                    connectedLeafNr=(int(x["name"][len(x["name"])-2:len(x["name"])])) #probably not the best way to do this
                except:
                    connectedLeafNr=(int(x["name"][len(x["name"])-1:len(x["name"])]))

        #provides the relevant subnet information
        relevantSubnet=subbnetList[0][node.host['switchpair']-1]

        #checking it he connected leaf is greater than the current leaf
        if connectedLeafNr>LeafNr: #!low leaf
            vlanIp=(relevantSubnet['subbnetID'][:-1]+"2") #changes the last number in the subnet to 2
            leafPriority=105

        else: #!high leaf
            vlanIp = relevantSubnet['subbnetID'][:-1]+"3"
            leafPriority=100
            
        
        standbyIp = relevantSubnet['subbnetID'][:-1]+"1"

        print("i am leaf",LeafNr)
        print("i am connected to leaf",connectedLeafNr, "\n")


        #TODO:
        #add all the interfaces pointing to spines to a tracking list
        #this is to decrement the priority of the hsrp
        #track 1 interface G0/0 line-protocol
        #no track 1
        


        #!fix vlan 10 you probably just have to add it in the 
        #? remember that the vlan interface should not be advertised to the spines bechause it should be tunneled
        commandList=[]
        for x in cdpNeigbourDirections:
            if "spine" in x:
                print(x)
                
        commandList.extend([f"vlan 1", f"interface vlan 1", f"ip address {vlanIp} 255.255.255.0" ,f"standby 1 ip {standbyIp}", f"standby 1 preempt", f"standby 1 priority {leafPriority}", f"no sh", f"exit"])

        test = node.run(task=netmiko_send_config, config_commands=commandList)
        print_result(test)

    #print(switchpair)
    


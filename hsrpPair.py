from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from Subbnetter import subbnetter
from tqdm import tqdm
import time
#required for the script to be run
#switches to be a part of a switchpair. example : switchpair: 1 under data in host.yaml
#switchpaires to be connected to each other
#leaf host names to be numbered

def hsrpPair(node): #main function of this script
    StartTime = time.time()
    pbar = tqdm(total=4)
    subbnetList=[]
    subbnetList.append(subbnetter(nettwork=f"192.168.2.0",
        nettworkReq=[
        {"numberOfSubbnets":10, "requiredHosts":255},
        ])) #makes 1 subbnets with 255 hosts each

    #constructs the interface information and running config information
    GatherStartTime=time.time()
    pbar.colour="yellow"
    pbar.set_description(f"{node.host}: facts gathered 1 of 2") #writes to the progress bar
    pbar.update() #updates the progress bar
    node.host["cdp"] = node.run(task=netmiko_send_command, command_string=("sh cdp nei de")).result #this is the interface information
    pbar.colour="yellow"
    pbar.set_description(f"{node.host}: facts gathered 2 of 2") #writes to the progress bar
    pbar.update() #updates the progress bar
    node.host["run"] = node.run(task=netmiko_send_command, command_string=("sh run"), enable=True).result #this is the running config
    GatherEndTime=time.time()

    hostnames = [i for i in range(len(node.host["cdp"])) if node.host["cdp"].startswith("Device ID:", i)] #finds the location of the device id
    interfaces = [i for i in range(len(node.host["cdp"])) if node.host["cdp"].startswith("Interface:", i)] #finds the location of the interface

    # puts the cdp information into a dictionary
    cdpNeigbourDirections=[]
    for x in range(len(hostnames)):
        hostname = (node.host["cdp"][hostnames[x]+11:hostnames[x]+24].split("\n")[0].split(".")[0]) #this is the hostname of the neigbour
        interface = (node.host["cdp"][interfaces[x]+11:interfaces[x]+30].split("\n")[0].split(".")[0].split(",")[0]) #this is the interface that the neigbour is connected to
        if hostname != "Switch": #this is to make sure that the hostname is not just a switch
            cdpNeigbourDirections.append({"name":hostname, "interface":interface})


    #check if self is in a switchpair and if so what is the switch in the pair
    try:
        switchpair=node.host['switchpair']
        if "hostname leaf" in node.host["run"]:
            leaf=True
        else:
            leaf=False
            pbar.colour="yellow"
            pbar.set_description(f"{node.host}: it is a router not needing config") #writes to the progress bar
            pbar.update() #updates the progress bar
            time.sleep(1)
            pbar.colour="green"
            pbar.update()

    except: #if not in a switchpair meaning it is a spine
        pbar.set_description(f"{node.host}: spine") #writes to the progress bar
        pbar.update() #updates the progress bar
        time.sleep(1)
        pbar.colour="green"
        pbar.update() #finishes the progress bar
        leaf=False

    if leaf==True: #if the node is not a spine
        #finds out what switchnumber the node is (code from subbnetter)
        locationOfQuote=node.host["run"].find(f"hostname leaf")
        LeafNr=int(node.host["run"][locationOfQuote+13:locationOfQuote+15].replace(" ","").replace("\n",""))
        
        #a loop to find leafs in the cdp neigbour list
        for x in cdpNeigbourDirections: #for every neigbour in the cdp neigbour list
            if "leaf" in x["name"]: #if the neigbour is a leaf
                try: #try to search if the number is over 9
                    connectedLeafNr=(int(x["name"][len(x["name"])-2:len(x["name"])])) #probably not the best way to do this
                except: #if not over 9
                    connectedLeafNr=(int(x["name"][len(x["name"])-1:len(x["name"])]))

        #provides the relevant subnet information
        relevantSubnet=subbnetList[0][node.host['switchpair']-1]

        #checking it he connected leaf is greater than the current leaf
        if connectedLeafNr>LeafNr: #if the connected leaf is greater than the current leaf
            vlanIp=(relevantSubnet['subbnetID'][:-1]+"2") #changes the last number in the subnet to 2
            leafPriority=105 #standby priority

        else: #if the connected leaf is less than the current leaf
            vlanIp = relevantSubnet['subbnetID'][:-1]+"3"
            leafPriority=100
        
        standbyIp = relevantSubnet['subbnetID'][:-1]+"1" #standby ip
        

        #? remember that the vlan interface should not be advertised to the spines bechause it should be tunneled¨
        #!potential problem is that if a entire spine is down it breakes this bechause it is a BOOL wich means that if two links go down on the main and only one on t he backup it will not fall back to the backup
        #! not a big problem, but just a thing to remember
        commandList=[("track 1 list boolean and")]
        counter = 2
        for x in cdpNeigbourDirections:
            if "spine" in x["name"]:
                commandList.extend([f"track {counter} interface {x['interface']} line-protocol"]) #adds the track command to the list
                commandList.extend([f"track 1", f"object {counter}"])
                counter += 1
                
        commandList.extend([f"vlan 1", f"interface vlan 1", f"ip address {vlanIp} 255.255.255.0" ,f"standby 1 ip {standbyIp}", f"standby 1 track 1 decrement 10", f"standby 1 preempt", f"standby 1 priority {leafPriority}", f"no sh", f"exit"])
        pbar.colour="yellow"
        pbar.set_description(f"{node.host}: sending configgs") #writes to the progress bar
        pbar.update() #updates the progress bar
        CommandStartTime=time.time()
        node.run(task=netmiko_send_config, config_commands=commandList) #sends the configs
        CommandEndTime=time.time()
        pbar.colour="green"
        pbar.set_description(f"{node.host}: done") #writes to the progress bar
        pbar.update() #updates the progress bar

    else: #if the node is a leaf
        commandList=[]
        GatherEndTime = 0
        GatherStartTime = 0
        CommandEndTime = 0
        CommandStartTime = 0

    EndTime=time.time()

    return len(commandList)+2, EndTime-StartTime, GatherEndTime-GatherStartTime, CommandEndTime-CommandStartTime

    #print(switchpair)
    


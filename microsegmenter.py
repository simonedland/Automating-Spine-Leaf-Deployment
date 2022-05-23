import time
from tqdm import tqdm
from Subbnetter import subbnetter
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result


#EXAMPLE OF HOW TO USE THE FUNCTION
#nr.run(task=MicroSegmenter,SegmentationIps="10.1",
#    SpineHostName="spine", 
#    LeafHostname="leaf", 
#    IpDomainName="simon")


def subbnetMicroSegmentListMaker(SegmentationIps):
    #this makes 10 subbnets with 64 microsegments (subbnets with 2 hosts) making it possible to have 10 spines and 64 leafs
    #if you need more spines you can always increase the loop amount

    subbnetList=[] #this is the list that will be returned
    for x in range(0,9): #makes 10 subbnets
        subbnetList.append(subbnetter(nettwork=f"{SegmentationIps}.{x}.0",
            nettworkReq=[
            {"numberOfSubbnets":64, "requiredHosts":2},
            ])) #makes 64 subbnets with 2 hosts each

    return subbnetList #returns the list



def MicroSegmenter(node, SegmentationIps="10.1", SpineHostName="spine", LeafHostname="leaf", IpDomainName="simon"): #this is the function that will be called by the nornir plugin. the segmentation ips only support assigning the first two octets of the ip.

    bar=tqdm(total=4, desc =str(node.host)) #this is the progress bar

    listOfSubbnets=subbnetMicroSegmentListMaker(SegmentationIps)#fetches the ip adress data for tyhe spine leaf copnnection

    #constructs the interface information and running config information
    #theese are stored in node.host[intf] and [self]
    bar.colour="yellow"
    bar.set_description(f"{node.host}: facts gathered 1 of 2") #writes to the progress bar
    bar.update() #updates the progress bar
    node.host["intf"] = node.run(task=netmiko_send_command, command_string=("sh cdp nei de")).result #this is the interface information
    bar.set_description(f"{node.host}: facts gathered 2 of 2") #writes to the progress bar
    bar.update() #updates the progress bar
    node.host["self"] = node.run(task=netmiko_send_command, command_string=("sh run"), enable=True).result #this is the running config
    
    
    #finds all the locations of the keywords device id and interface
    #this information is on the cdp neigbour and is information about the neigbor bechause we are making a connection to the neigbour
    hostnames = [i for i in range(len(node.host["intf"])) if node.host["intf"].startswith("Device ID:", i)] #finds the location of the device id
    interfaces = [i for i in range(len(node.host["intf"])) if node.host["intf"].startswith("Interface:", i)] #finds the location of the interface
    #constructs a list of dictionaries with the values of hostname and what interface it is connected to

    if len(SpineHostName) >= len(LeafHostname): #this is to check the spine hostname is longer than the leaf hostname
        longestname = len(SpineHostName) #sets the longest name to the spine hostname
    else:
        longestname = len(LeafHostname)
    

    cdpNeigbourDirections=[]
    domNameLen=len(IpDomainName)
    for x in range(len(hostnames)):
        hostname = (node.host["intf"][hostnames[x]+domNameLen+6:hostnames[x]+domNameLen+longestname+14].split("\n")[0].split(".")[0]) #this is the hostname of the neigbour
        interface = (node.host["intf"][interfaces[x]+domNameLen+6:interfaces[x]+domNameLen+longestname+20].split("\n")[0].split(".")[0].split(",")[0]) #this is the interface that the neigbour is connected to
        if hostname != "Switch":
            cdpNeigbourDirections.append({"name":hostname, "interface":interface}) #adds the hostname and interface to the list

    #finds out if the relevant switch is a spine or leaf
    if f"hostname {LeafHostname}" in node.host["self"]: #checks if it self is a leaf
        LenOfHostName=len(LeafHostname)
        LenOfNeigborName=len(SpineHostName)
        commandlist=[f'ip routing', f'int lo 0'] # adds the commands to add the loopback interface to a 0 of eigrp in the creation of the command list
        for neigbor in cdpNeigbourDirections: # if it is a leaf it loops trough al the cdp neigbor information
            if SpineHostName in neigbor["name"]: # if it finds spine it wil do the following
                try: # finds out what number of spine it is the reason we do it this way is bechause we dont know if it is spine 20 or 2 so we try to convert the biggest first in to a string
                    spineNr=int(neigbor["name"][LenOfNeigborName:LenOfNeigborName+2])
                except:
                    spineNr=int(neigbor["name"][LenOfNeigborName:LenOfNeigborName+1])
                locationOfQuote=node.host["self"].find(f"hostname {LeafHostname}") # finds out where it self says what leaf it is in the running config by looking for the hostname
                LeafNr=int(node.host["self"][locationOfQuote+LenOfHostName+9:locationOfQuote+LenOfHostName+11].replace(" ","")) # converts the last part of the hostname in to a int example: leaf7 = 7
                relevantSubbnet=listOfSubbnets[spineNr-1][LeafNr-1]#naming of the spines and leafs starts at 1 but the lists start at 0
                MyIp=(f"{relevantSubbnet['broadcast'].split('.')[0]}.{relevantSubbnet['broadcast'].split('.')[1]}.{relevantSubbnet['broadcast'].split('.')[2]}.{int(relevantSubbnet['broadcast'].split('.')[3])-1}")#places it self one IP under the broadcast
                
                #prepaires the list of commands needed to add itself to eigrp and find the correct ip adress in the microsegment
                commandlist.extend([f"int {neigbor['interface']}",f"no switch",f"no sh",f"ip add {MyIp} {relevantSubbnet['mask']}",f"router eigrp 1",f"network {relevantSubbnet['subbnetID']} {relevantSubbnet['mask']}"])

        #runns the list of commands and prints the result
        bar.set_description(f"{node.host}: sending commands")
        bar.update()
        node.run(task=netmiko_send_config, config_commands=commandlist) #runs the command list


    elif f"hostname {SpineHostName}" in node.host["self"]:
        LenOfHostName=len(SpineHostName)
        LenOfNeigborName=len(LeafHostname)
        commandlist=[f'ip routing', f'int lo 0']
        for neigbor in cdpNeigbourDirections:
            if LeafHostname in neigbor["name"]: #if it finds leaf it will do the following
                try:
                    leafNr = int(neigbor["name"][LenOfNeigborName:LenOfNeigborName+2])
                except:
                    leafNr = int(neigbor["name"][LenOfNeigborName:LenOfNeigborName+1])
            else:
                pass #if it is not a leaf it will do nothing
            locationOfQuote=node.host["self"].find(f"hostname {SpineHostName}")
            SpineNr=int(node.host["self"][locationOfQuote+LenOfHostName+9:locationOfQuote+LenOfHostName+11].replace(" ",""))
            relevantSubbnet=listOfSubbnets[SpineNr-1][leafNr-1]
            MyIp=(f"{relevantSubbnet['subbnetID'].split('.')[0]}.{relevantSubbnet['subbnetID'].split('.')[1]}.{relevantSubbnet['subbnetID'].split('.')[2]}.{int(relevantSubbnet['subbnetID'].split('.')[3])+1}")
            
            commandlist.extend([f"int {neigbor['interface']}",f"no switch",f"no sh",f"ip add {MyIp} {relevantSubbnet['mask']}",f"router eigrp 1",f"network {relevantSubbnet['subbnetID']} {relevantSubbnet['mask']}"])
        
        bar.set_description(f"{node.host}: sending commands")
        bar.update()
        test=node.run(task=netmiko_send_config, config_commands=commandlist)
        print_result(test)
    
    bar.set_description(f"{node.host}: done")
    bar.colour="green"
    bar.update()
    time.sleep(2)
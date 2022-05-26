from microsegmenter import MicroSegmenter
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
import time
from nornir_utils.plugins.functions import print_result


#a function that should configgure the edge leafs to be the default gateway for the WAN
#this function should also configgure the routers to be the default gateway for the WAN

#? to match the ip range of the connected leafs to the connected edge routers i can say that it is connected to leaf group X
#config the nat translation for the edge routers


def ConfigEdgeLeaf(node):
    StartTime = time.time()
    #this is the configuration of the edge leafs
    Segmenter = node.run(task=MicroSegmenter,
            SegmentationIps="10.4",
            SpineHostName="router", 
            LeafHostname="leaf", 
            IpDomainName="simon",
            UseOSPF=True,)

    GatherTimeStart = time.time()
    node.host["self"] = node.run(task=netmiko_send_command, command_string=("sh run"), enable=True).result
    GatherTimeEnd = time.time()

    #if it is a router i should add the nat translation and the default gateway
    if "hostname router" in node.host["self"]:
        #!not very modular
        CommandList=[]
        CommandList.extend(["router ospf 1" ,"int g0/2","ip addres dhcp","ip nat outside", "ip ospf 1 a 0", "int g0/0","ip nat inside","int g0/1","ip nat inside", "exit", "access-list 1 permit any", "ip nat inside source list 1 interface g0/2 overload"])
        CommandTimeStart = time.time()
        node.run(task=netmiko_send_config, config_commands=CommandList)
        CommandTimeEnd = time.time()
    
    else:
        CommandList=[]

    EndTime = time.time()
    return len(CommandList)+Segmenter[0].result[0], EndTime-StartTime, (GatherTimeEnd-GatherTimeStart)+Segmenter[0].result[2], (CommandTimeEnd-CommandTimeStart)+Segmenter[0].result[3]
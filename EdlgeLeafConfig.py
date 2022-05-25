from distutils.cmd import Command
from microsegmenter import MicroSegmenter
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config


#a function that should configgure the edge leafs to be the default gateway for the WAN
#this function should also configgure the routers to be the default gateway for the WAN

#? to match the ip range of the connected leafs to the connected edge routers i can say that it is connected to leaf group X
#config the nat translation for the edge routers


def ConfigEdgeLeaf(node):
    #this is the configuration of the edge leafs
    node.run(task=MicroSegmenter,
            SegmentationIps="10.4",
            SpineHostName="router", 
            LeafHostname="leaf", 
            IpDomainName="simon",
            UseOSPF=True,)
    
    node.host["self"] = node.run(task=netmiko_send_command, command_string=("sh run"), enable=True).result

    #if it is a router i should add the nat translation and the default gateway
    if "hostname router" in node.host["self"]:
        #locationOfQuote=node.host["self"].find(f"hostname router")
        #LeafNr=int(node.host["self"][locationOfQuote+15:locationOfQuote+16].replace(" ","").replace("\n",""))
        #this is the configuration of the edge routers
        #!not very modular
        CommandList=[]
        CommandList.extend(["ip route 0.0.0.0 0.0.0.0 192.168.1.1","router ospf 1", "default-information originate always" ,"int g0/2","ip addres dhcp","ip nat outside", "no ip ospf 1 a 0", "int g0/0","ip nat inside","int g0/1","ip nat inside", "exit", "access-list 1 permit 192.168.0.0 0.0.255.255", "ip nat inside source list 1 interface g0/2 overload"])
        node.run(task=netmiko_send_config, config_commands=CommandList)
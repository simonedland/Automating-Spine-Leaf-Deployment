#import my own functions
from lib2to3.pytree import Leaf
from microsegmenter import MicroSegmenter
from CopRunStart import SaveRunningToStart
from pingTest import ping
from resett import resetter, resettHostName
from hsrpPair import hsrpPair
from VPNMesh import vpnMaker


#import other functions
from nornir import InitNornir
from nornir.core.filter import F
from tqdm import tqdm
import time

#todo:
#enable CDP at the start of the script
#expand on the resetter function to reset the vlans
#figgure out how to use vpc
#make a vpn tunnel maker
#configg the routers/edge leafs connected to WAN
#! tricky hsrp on the gateway leafs and touters
#figgure out how to use redundancy with the routers
#where to putt DHCP server if eaven needed
#add a command counter and a average commands per second counter
#!DHCP FAILOVER
#livestream telemetry
#argument for having the link between the switches = if someone want single link
#L2TP VPN
#redo the storage of the running config and interface config in adition to the cdp
#maby store it in the nornir object


#note to self:
#CDP should be disabled after deployment is done
#this is bechause it is recomended by the Cisco documentation
#i am not going to be using VPC due to my computer not having the capacity to emulate it

#optional: tftp ssh config deployment using option 82 (optional)
#optional: mac adress reserve ip adress based
#optional: client side almoaste equal settup, only difrence is in host. yaml file

startTime=time.time() #this is the start time of the program

def main():

    bringDown=False #this is the option to bring down the network
    oneHost=False #if you want to run on one host, set this to true
    useMinGroup=False #reduce the number of hosts to the minimum required for the test
    testNew=False #if you want to test the new code, set this to true

    nr = InitNornir(config_file="config.yaml") #this is the nornir object
    if oneHost:
        nr = nr.filter(name="spine1.cmh") #this is the nornir object with only one host
    if useMinGroup:
        nr = nr.filter(has_parent_group="minGroup")

    if bringDown: #this is the option to bring down the network
        pbar = tqdm(total=5)
        pbar.set_description("pinging hosts")
        pbar.colour="yellow"
        pbar.update()

        nr.run(task=ping) #this is the ping test
        pbar.set_description("configuring hostnames and ip domain name")
        pbar.update()

        nr.run(task=resettHostName)
        nr = InitNornir(config_file="config.yaml") #re initialize the nornir object due to changes in hostname breaking the rest of the program if not reinitialized
        if oneHost: #if you want to run on one host, set this to true
            nr = nr.filter(name="spine1.cmh") #this is the nornir object with only one host
        if useMinGroup: #reduce the number of hosts to the minimum required for the test
            nr = nr.filter(F(has_parent_group="minGroup"))

        pbar.set_description("resetting interfaces")
        pbar.update()

        nr.run(task=resetter) #this is the resetter function

        pbar.set_description("done resetting interfaces")
        pbar.update()

    elif testNew: #if you want to test the new code, set this to true
        pbar = tqdm(total=1)
        leafs = len(nr.inventory.children_of_group("leaf")) #this is the number of leafs in the network
        spines = len(nr.inventory.children_of_group("spine"))
        nr.run(task=vpnMaker, NrOfLeafs=leafs, NrOfSpines=spines) #this is the vpn mesh function

    else: #runns the settup
        pbar = tqdm(total=3)
        nr.run(task=ping)
        pbar.colour="yellow"

        pbar.set_description("configuring hostnames and ip domain name")
        pbar.update()

        nr.run(task=MicroSegmenter,SegmentationIps="10.0",
            SpineHostName="spine", 
            LeafHostname="leaf", 
            IpDomainName="simon")
        
        pbar.set_description("configging HSRP")
        pbar.update()
        nr.run(task=hsrpPair) #runns the hsrp pair setup (should filter this to only runn on leafs)


    pbar.set_description("saving running config to start config")
    nr.run(task=SaveRunningToStart)


    pbar.colour="green"
    pbar.set_description("done")
    pbar.update()
    pbar.close()

    #rebooting will cause a error
    #print("rebooting")
    #nr.run(task=netmiko_send_command, command_string="reload", enable=True, use_timing=True)
    #nr.run(task=netmiko_send_command, command_string="y", enable=True, use_timing=True, ignore_errors=True)

main() #run the main function


print(f"\n\n\n\n\n\n\n\n\n\nthe script took {time.time()-startTime} seconds") #prints how long the script took to run
#import my own functions
from lib2to3.pytree import Leaf
from microsegmenter import MicroSegmenter
from CopRunStart import SaveRunningToStart
from pingTest import ping
from resett import resetter, resettHostName
from hsrpPair import hsrpPair
from VPNMesh import vpnMaker
from CDPControll import TurnOfCDP, TurnOnCDP
from EdlgeLeafConfig import ConfigEdgeLeaf

#import other functions
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir.core.filter import F
from tqdm import tqdm
import time

#todo:
#where to putt DHCP server if eaven needed
#add a command counter and a average commands per second counter #?threads add the total to a file??
#!DHCP FAILOVER
#!improove the resetter to reset the standby and logic groups

#note to self:
#CDP should be disabled after deployment is done
#this is bechause it is recomended by the Cisco documentation
#i am not going to be using VPC due to my computer not having the capacity to emulate it

#!no time for this
#figgure out how to use vpc
#L2TP VPN
#redo the storage of the running config and interface config in adition to the cdp
#maby store it in the nornir object
#optional: tftp ssh config deployment using option 82 (optional)
#optional: mac adress reserve ip adress based
#optional: client side almoaste equal settup, only difrence is in host. yaml file
#optional: add a function to check if the router is connected to the WAN
#optional: telemerty thinggy

#lock if not comma??

startTime=time.time() #this is the start time of the program

def main():

    bringDown=False #this is the option to bring down the network
    oneHost=False #if you want to run on one host, set this to true
    useMinGroup=False #reduce the number of hosts to the minimum required for the test
    testNew=True #if you want to test the new code, set this to true

    nr = InitNornir(config_file="config.yaml") #this is the nornir object
    if oneHost:
        nr = nr.filter(name="leaf1.cmh") #this is the nornir object with only one host
    if useMinGroup:
        nr = nr.filter(has_parent_group="minGroup")

    if bringDown: #this is the option to bring down the network
        pbar = tqdm(total=7)
        pbar.colour="yellow"
        pbar.update()

        pbar.set_description("turning on cdp")
        nr.run(task=TurnOnCDP) #turn on CDP
        pbar.update()

        pbar.set_description("pinging hosts")
        nr.run(task=ping) #this is the ping test
        pbar.update()

        pbar.set_description("configuring hostnames and ip domain name")
        nr.run(task=resettHostName)
        nr = InitNornir(config_file="config.yaml") #re initialize the nornir object due to changes in hostname breaking the rest of the program if not reinitialized
        if oneHost: #if you want to run on one host, set this to true
            nr = nr.filter(name="spine1.cmh") #this is the nornir object with only one host
        if useMinGroup: #reduce the number of hosts to the minimum required for the test
            nr = nr.filter(F(has_parent_group="minGroup"))
        pbar.update()

        pbar.set_description("resetting interfaces")
        nr.run(task=resetter) #this is the resetter function
        pbar.update()

        pbar.set_description("turning off cdp")
        nr.run(task=TurnOfCDP) #turn on CDP
        pbar.update()

    elif testNew: #if you want to test the new code, set this to true

        pbar = tqdm(total=3)
        pbar.set_description("turning on cdp")
        nr.run(task=TurnOnCDP) #turn on CDP
        pbar.update()

        pbar.set_description("turning off cdp")
        nr.run(task=TurnOfCDP) #turn on CDP
        pbar.update()


    else: #runns the settup
        pbar = tqdm(total=9)
        pbar.colour="yellow"

        pbar.set_description("pinging hosts")
        nr.run(task=ping)
        pbar.update()

        pbar.set_description("resetting host names")
        nr.run(task=resettHostName)
        nr = InitNornir(config_file="config.yaml") #re initialize the nornir object due to changes in hostname breaking the rest of the program if not reinitialized
        if oneHost: #if you want to run on one host, set this to true
            nr = nr.filter(name="spine1.cmh") #this is the nornir object with only one host
        if useMinGroup: #reduce the number of hosts to the minimum required for the test
            nr = nr.filter(F(has_parent_group="minGroup"))
        pbar.update()


        pbar.set_description("turning on cdp")
        nr.run(task=TurnOnCDP) #turn on CDP
        pbar.update()

        pbar.set_description("configuring EIGRP underlay")
        nr.run(task=MicroSegmenter,SegmentationIps="10.0",
            SpineHostName="spine", 
            LeafHostname="leaf", 
            IpDomainName="simon")
        pbar.update()

        
        pbar.set_description("configging HSRP")
        nr.run(task=hsrpPair) #runns the hsrp pair setup (should filter this to only runn on leafs)
        pbar.update()


        pbar.set_description("Setting up VPN Mesh")
        leafs = len(nr.inventory.children_of_group("leaf")) #this is the number of leafs in the network
        spines = len(nr.inventory.children_of_group("spine"))
        nr.run(task=vpnMaker, NrOfLeafs=leafs, NrOfSpines=spines) #this is the vpn mesh function
        pbar.update()


        pbar.set_description("configuring edge leafs")
        edgeNodes = nr.filter(F(groups__contains="edge")) #this is the nornir object with only the edge nodes
        edgeNodes.run(task=ConfigEdgeLeaf)
        pbar.update()


        pbar.set_description("turning off cdp")
        nr.run(task=TurnOfCDP) #turn on CDP
        pbar.update()


    #pbar.set_description("saving running config to start config")
    #nr.run(task=SaveRunningToStart)


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
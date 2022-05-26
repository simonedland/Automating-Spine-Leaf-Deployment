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
#display stats at the end of the script
#display average commands per second
#where to putt DHCP server if eaven needed
#!DHCP FAILOVER
#!improove the resetter to reset the standby and logic groups

#note to self:
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



startTime=time.time() #this is the start time of the program

def main():

    bringDown=True #this is the option to bring down the network
    oneHost=False #if you want to run on one host, set this to true
    useMinGroup=False #reduce the number of hosts to the minimum required for the test
    testNew=False #if you want to test the new code, set this to true

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



        pbar = tqdm(total=1)
        edgeNodes = nr.filter(F(groups__contains="edge")) #this is the nornir object with only the edge nodes
        test=edgeNodes.run(task=ConfigEdgeLeaf) #this is the vpn mesh function

        tot=0
        avgTime=0
        for x in test:
            pass
            print(test[x].result)
            tot+=test[x].result[0]
            avgTime+=test[x].result[1]
        print(tot)
        avgTime=avgTime/len(test)
        print(avgTime)

        pbar.update()


    else: #runns the settup
        pbar = tqdm(total=9)
        pbar.colour="yellow"

        tot=0

        pbar.set_description("pinging hosts")
        PingavgTime=0
        PingCount = nr.run(task=ping)
        for x in PingCount:
            print(PingCount[x].result)
            PingavgTime+=PingCount[x].result[1]
            tot+=PingCount[x].result[0]
        print(tot)
        PingavgTime=PingavgTime/len(PingCount)
        print(PingavgTime)
        pbar.update()


        pbar.set_description("resetting host names")
        HostAvghTime = 0
        HostCount = nr.run(task=resettHostName)
        for x in HostCount:
            print(HostCount[x].result)
            HostAvghTime+=HostCount[x].result[1]
            tot+=HostCount[x].result[0]
        print(tot)
        HostAvghTime=HostAvghTime/len(HostCount)
        print(HostAvghTime)
        nr = InitNornir(config_file="config.yaml") #re initialize the nornir object due to changes in hostname breaking the rest of the program if not reinitialized
        pbar.update()


        pbar.set_description("turning on cdp")
        CDPavgTime = 0
        CDPaverageComandTime = 0
        CDPCount = nr.run(task=TurnOnCDP)
        for x in CDPCount:
            print(CDPCount[x].result)
            CDPavgTime+=CDPCount[x].result[1]
            tot+=CDPCount[x].result[0]
            CDPaverageComandTime+=CDPCount[x].result[2]
        print(tot)
        CDPavgTime=CDPavgTime/len(CDPCount)
        print(CDPavgTime)
        CDPaverageComandTime=CDPaverageComandTime/len(CDPCount)
        print(CDPaverageComandTime)
        pbar.update()


        pbar.set_description("configuring EIGRP underlay")
        EIGRPavgTime = 0
        GatherAverageTime = 0
        CommandAverage=0
        EIGRPcount = nr.run(task=MicroSegmenter,SegmentationIps="10.0",
            SpineHostName="spine", 
            LeafHostname="leaf", 
            IpDomainName="simon")
        for x in EIGRPcount:
            print(EIGRPcount[x].result)
            EIGRPavgTime+=EIGRPcount[x].result[1]
            tot+=EIGRPcount[x].result[0]
            Gathertime=EIGRPcount[x].result[2]
            CommandAverage+=EIGRPcount[x].result[3]
        print(tot)
        EIGRPavgTime=EIGRPavgTime/len(EIGRPcount)
        print(EIGRPavgTime)
        GatherAverageTime=Gathertime/len(EIGRPcount)
        print(GatherAverageTime)
        CommandAverage=CommandAverage/len(EIGRPcount)
        print(CommandAverage)
        pbar.update()

        
        pbar.set_description("configging HSRP")
        HSRPavgTime = 0
        HSRPGatherTime = 0
        HSRPaverageComandTime = 0
        HSRPcount = nr.run(task=hsrpPair)
        for x in HSRPcount:
            print(HSRPcount[x].result)
            HSRPavgTime+=HSRPcount[x].result[1]
            tot+=HSRPcount[x].result[0]
            HSRPGatherTime+=HSRPcount[x].result[2]
            HSRPaverageComandTime+=HSRPcount[x].result[3]
        print(tot)
        HSRPavgTime=HSRPavgTime/len(HSRPcount)
        print(HSRPavgTime)
        HSRPGatherTime=HSRPGatherTime/len(HSRPcount)
        print(HSRPGatherTime)
        HSRPaverageComandTime=HSRPaverageComandTime/len(HSRPcount)
        print(HSRPaverageComandTime)
        pbar.update()


        pbar.set_description("Setting up VPN Mesh")
        leafs = len(nr.inventory.children_of_group("leaf")) #this is the number of leafs in the network
        spines = len(nr.inventory.children_of_group("spine"))
        VPNcpount = nr.run(task=vpnMaker, NrOfLeafs=leafs, NrOfSpines=spines) #this is the vpn mesh function
        VPNGathertime = 0
        VPNcommandTime = 0
        VPNavgTime=0
        for x in VPNcpount:
            print(VPNcpount[x].result)
            tot+=VPNcpount[x].result[0]
            VPNavgTime+=VPNcpount[x].result[1]
            VPNGathertime+=VPNcpount[x].result[2]
            VPNcommandTime+=VPNcpount[x].result[3]
        print(tot)
        VPNavgTime=VPNavgTime/len(VPNcpount)
        print(VPNavgTime)
        VPNGathertime=VPNGathertime/len(VPNcpount)
        print(VPNGathertime)
        VPNcommandTime=VPNcommandTime/len(VPNcpount)
        print(VPNcommandTime)
        pbar.update()


        pbar.set_description("configuring edge leafs")
        edgeNodes = nr.filter(F(groups__contains="edge")) #this is the nornir object with only the edge nodes
        Edgecount = edgeNodes.run(task=ConfigEdgeLeaf)
        EdgeavgTime = 0
        for x in Edgecount:
            print(Edgecount[x].result)
            tot+=Edgecount[x].result[0]
            EdgeavgTime+=Edgecount[x].result[1]
        print(tot)
        EdgeavgTime=EdgeavgTime/len(Edgecount)
        print(EdgeavgTime)
        pbar.update()


        pbar.set_description("turning off cdp")
        nr.run(task=TurnOfCDP) #turn on CDP
        ofCdpcount = nr.run(task=TurnOfCDP)
        ofCdpavgTime = 0
        for x in ofCdpcount:
            print(ofCdpcount[x].result)
            tot+=ofCdpcount[x].result[0]
            ofCdpavgTime+=ofCdpcount[x].result[1]
        print(tot)
        ofCdpavgTime=ofCdpavgTime/len(ofCdpcount)
        print(ofCdpavgTime)
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
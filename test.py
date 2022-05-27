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
#?rename variables
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

    bringDown=False #this is the option to bring down the network
    testNew=False #if you want to test the new code, set this to true


    tot=0
    HostAvghTime = 0
    hostcommands = 0
    PingavgTime=0
    CDPavgTime = 0
    CDPaverageComandTime = 0
    CDPcommands = 0
    EdgeavgTime = 0
    EdgeGatherTime = 0
    EdgeCommandTime = 0
    EdgeCommandCount=0
    VPNGathertime = 0
    VPNcommandTime = 0
    VPNavgTime=0
    VPNGatherd=0
    VPNcommands=0
    VPNCommandCount=0
    EIGRPavgTime = 0
    GatherAverageTime = 0
    CommandAverage=0
    EIGRPcommands = 0
    HSRPavgTime = 0
    HSRPGatherTime = 0
    HSRPaverageComandTime = 0
    HSRPGatherd=0
    HSRPCommands=0
    HSRPCommandCount=0
    ofCdpavgTime = 0

    
    nr = InitNornir(config_file="config.yaml") #this is the nornir object

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

        pbar.set_description("pinging hosts")
        PingCount = nr.run(task=ping)
        for x in PingCount:
            PingavgTime+=PingCount[x].result[1]
            tot+=PingCount[x].result[0]
        PingavgTime=PingavgTime/len(PingCount)
        pbar.update()


        pbar.set_description("resetting host names")
        HostCount = nr.run(task=resettHostName)
        for x in HostCount:
            HostAvghTime+=HostCount[x].result[1]
            hostcommands+=HostCount[x].result[0]
        tot+=hostcommands
        HostAvghTime=HostAvghTime/len(HostCount)
        hostPScommands=hostcommands/HostAvghTime
        nr = InitNornir(config_file="config.yaml") #re initialize the nornir object due to changes in hostname breaking the rest of the program if not reinitialized
        pbar.update()


        pbar.set_description("turning on cdp")
        CDPCount = nr.run(task=TurnOnCDP)
        for x in CDPCount:
            CDPavgTime+=CDPCount[x].result[1]
            CDPcommands+=CDPCount[x].result[0]
            CDPaverageComandTime+=CDPCount[x].result[2]
        tot+=CDPcommands
        CDPavgTime=CDPavgTime/len(CDPCount)
        CDPaverageComandTime=CDPaverageComandTime/len(CDPCount)
        CDPPScommands=CDPcommands/CDPaverageComandTime
        pbar.update()


        pbar.set_description("configuring EIGRP underlay")
        EIGRPcount = nr.run(task=MicroSegmenter,SegmentationIps="10.0",
            SpineHostName="spine", 
            LeafHostname="leaf", 
            IpDomainName="simon")
        for x in EIGRPcount:
            EIGRPavgTime+=EIGRPcount[x].result[1]
            EIGRPcommands+=EIGRPcount[x].result[0]
            Gathertime=EIGRPcount[x].result[2]
            CommandAverage+=EIGRPcount[x].result[3]
        tot+=EIGRPcommands
        EIGRPavgTime=EIGRPavgTime/len(EIGRPcount)
        GatherAverageTime=Gathertime/len(EIGRPcount)
        CommandAverage=CommandAverage/len(EIGRPcount)
        EIGRPPScommands=EIGRPcommands/CommandAverage
        pbar.update()

        
        pbar.set_description("configging HSRP")
        HSRPcount = nr.run(task=hsrpPair)
        for x in HSRPcount:
            HSRPavgTime+=HSRPcount[x].result[1]
            HSRPCommandCount+=HSRPcount[x].result[0]
            NodeHSRPTime=HSRPcount[x].result[2]
            if NodeHSRPTime != 0:
                HSRPGatherTime+=HSRPcount[x].result[2]
                HSRPGatherd+=1
            NodeHSRPTime=HSRPcount[x].result[3]
            if NodeHSRPTime != 0:
                HSRPaverageComandTime+=HSRPcount[x].result[3]
                HSRPCommands+=1
        tot+=HSRPCommandCount
        HSRPavgTime=HSRPavgTime/len(HSRPcount)
        HSRPGatherTime=HSRPGatherTime/HSRPGatherd
        HSRPaverageComandTime=HSRPaverageComandTime/HSRPCommands
        HSRPPScommands=HSRPCommandCount/HSRPaverageComandTime
        pbar.update()


        pbar.set_description("Setting up VPN Mesh")
        leafs = len(nr.inventory.children_of_group("leaf")) #this is the number of leafs in the network
        spines = len(nr.inventory.children_of_group("spine"))
        VPNcpount = nr.run(task=vpnMaker, NrOfLeafs=leafs, NrOfSpines=spines) #this is the vpn mesh function
        for x in VPNcpount:
            VPNCommandCount+=VPNcpount[x].result[0]
            VPNavgTime+=VPNcpount[x].result[1]
            NodeVPNTime=VPNcpount[x].result[2]
            if NodeVPNTime != 0:
                VPNGathertime+=VPNcpount[x].result[2]
                VPNGatherd+=1
            NodeVPNTime=VPNcpount[x].result[3]
            if NodeVPNTime != 0:
                VPNcommandTime+=VPNcpount[x].result[3]
                VPNcommands+=1
        tot+=VPNCommandCount
        VPNavgTime=VPNavgTime/len(VPNcpount)
        VPNGathertime=VPNGathertime/VPNGatherd
        VPNcommandTime=VPNcommandTime/VPNcommands
        VPNPScommands=VPNCommandCount/VPNcommandTime
        pbar.update()


        pbar.set_description("configuring edge leafs")
        edgeNodes = nr.filter(F(groups__contains="edge")) #this is the nornir object with only the edge nodes
        Edgecount = edgeNodes.run(task=ConfigEdgeLeaf)
        for x in Edgecount:
            EdgeCommandCount+=Edgecount[x].result[0]
            EdgeavgTime+=Edgecount[x].result[1]
            EdgeGatherTime+=Edgecount[x].result[2]
            EdgeCommandTime+=Edgecount[x].result[3]
        tot+=EdgeCommandCount
        EdgeavgTime=EdgeavgTime/len(Edgecount)
        EdgeGatherTime=EdgeGatherTime/len(Edgecount)
        EdgeCommandTime=EdgeCommandTime/len(Edgecount)
        EdgePScommands=EdgeCommandCount/EdgeCommandTime
        pbar.update()


        pbar.set_description("turning off cdp")
        nr.run(task=TurnOfCDP) #turn on CDP
        ofCdpcount = nr.run(task=TurnOfCDP)
        for x in ofCdpcount:
            tot+=ofCdpcount[x].result[0]
            ofCdpavgTime+=ofCdpcount[x].result[1]
        ofCdpavgTime=ofCdpavgTime/len(ofCdpcount)
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

    print(f"\n\n\n\n\n\n\n\n\n\ntime spent on average pinging: {PingavgTime}")
    print(f"time spent configuring host information: {HostAvghTime}, sending a total command count of {hostcommands}, command PS count {hostPScommands}")
    print(f"time spent configuring EIGRP: {EIGRPavgTime}, sending a total command count of {EIGRPcommands}, command PS count {EIGRPPScommands} using a average of {GatherAverageTime} on gathering information")
    print(f"time spent configuring CDP: {CDPavgTime}, sending a total command count of {CDPcommands}, command PS count {CDPPScommands}")
    print(f"time spent configuring HSRP: {HSRPavgTime}, sending a total command count of {HSRPCommandCount}, command PS count {HSRPPScommands}")
    print(f"time spent configuring VPN Mesh: {VPNavgTime}, sending a total command count of {VPNCommandCount}, command PS count {VPNPScommands}")
    print(f"time spent configuring edge leafs: {EdgeavgTime}, sending a total command count of {EdgeCommandCount}, command PS count {EdgePScommands}")
    print(f"time spent turning off cdp: {ofCdpavgTime}")
    print(f"total command PS: {(hostPScommands+EIGRPPScommands+CDPPScommands+HSRPPScommands+VPNPScommands+EdgePScommands)/6}")
    print(f"total commands sent: {tot}")



main() #run the main function


print(f"the script took {time.time()-startTime} seconds") #prints how long the script took to run
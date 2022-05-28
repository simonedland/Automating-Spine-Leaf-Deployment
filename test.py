#import my own functions
from microsegmenter import MicroSegmenter
from CopRunStart import SaveRunningToStart
from pingTest import ping
from resett import resetter, resettHostName
from hsrpPair import hsrpPair
from VPNMesh import vpnMaker
from CDPControll import TurnOfCDP, TurnOnCDP
from EdlgeLeafConfig import ConfigEdgeLeaf
from Subbnetter import subbnetter
from DHCPControll import AddDHCPPools

#import other functions
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir.core.filter import F
from tqdm import tqdm
import time

#todo:
#!FIX WHATEVER THE FUCK IS WRONG WITH THE VPN MESH THAT MAKES IT NON EKSTENSIBLE! 
#///!FIX  HSRP AND LEAF VLAN 1 SCRIPT!!! this was a configg error in host file
#!MAKE THE SCRIPT ABLE TO RUNN WITHOUT THE NEED OF EDGE SWITCHES!
#!RESETTER
#progressbar for DHCP
#nicify the outputt by rounding the numbers
#!improove the resetter to reset the standby and logic groups
#find out a nice way to display constructive outputt while the script is running
#look at ways to redo the storage of the fetch to prevent the script from gathering the same data many times 


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
    testNew=False #if you want to test the new code, set this to true


    tot=0
    Host_Conf_Avg_Time = 0
    Host_Config_command_count = 0
    Ping_Avg_Time=0
    CDP_AvgTime = 0
    CDP_Average_Comand_Time = 0
    CDP_Command_Count = 0
    Edge_AVG_Time = 0
    Edge_AVG_Gather_Time = 0
    Edge_AVG_Command_Time = 0
    Edge_Command_Count=0
    VPN_AVG_Gather_Time = 0
    VPN_AVG_Command_Time = 0
    VPN_Avg_Time=0
    VPN_Time_Gather_Count=0
    VPN_Command_Time_Counter=0
    VPN_Command_Count=0
    EIGRP_Avg_Time = 0
    EIGRP_AVG_Gather_Time = 0
    EIGRP_AVG_Command_Time=0
    EIGRP_Command_Count = 0
    HSRP_AVG_Time = 0
    HSRP_AVG_Gather_Time = 0
    HSRP_Average_Comand_Time = 0
    HSRP_Gather_Count=0
    HSRP_Command_Time_counter=0
    HSRP_Command_Count=0
    ofCdp_AvgTime = 0
    DHCP_AVG_Command_Time = 0
    DHCP_AVG_Gather_Time = 0
    DHCP_AVG_Time = 0
    DHCP_Command_Count = 0


    
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
        leafs = len(nr.inventory.children_of_group("leaf")) #this is the number of leafs in the network
        spines = len(nr.inventory.children_of_group("spine"))
        VPN_Node = nr.run(task=vpnMaker, NrOfLeafs=leafs, NrOfSpines=spines) #this is the vpn mesh function
        for x in VPN_Node:
            VPN_Command_Count+=VPN_Node[x].result[0]
            VPN_Avg_Time+=VPN_Node[x].result[1]
            Node_VPN_Gather_Time=VPN_Node[x].result[2]
            if Node_VPN_Gather_Time != 0:
                VPN_AVG_Gather_Time+=VPN_Node[x].result[2]
                VPN_Time_Gather_Count+=1
            Node_VPN_Command_Time=VPN_Node[x].result[3]
            if Node_VPN_Command_Time != 0:
                VPN_AVG_Command_Time+=VPN_Node[x].result[3]
                VPN_Command_Time_Counter+=1
        tot+=VPN_Command_Count
        VPN_Avg_Time=VPN_Avg_Time/len(VPN_Node)
        VPN_AVG_Gather_Time=VPN_AVG_Gather_Time/VPN_Time_Gather_Count
        VPN_AVG_Command_Time=VPN_AVG_Command_Time/VPN_Command_Time_Counter
        VPN_AVG_Commands_Per_Sec=VPN_Command_Count/VPN_AVG_Command_Time

        print(VPN_Node["leaf1.cmh"].result[5])
        for y in VPN_Node["leaf1.cmh"].result[4]:
            print(y)
        pbar.update()

    else: #runns the settup
        pbar = tqdm(total=10)
        pbar.colour="yellow"

        pbar.set_description("pinging hosts")
        Ping_Node = nr.run(task=ping)
        for x in Ping_Node:
            Ping_Avg_Time+=Ping_Node[x].result[1]
            tot+=Ping_Node[x].result[0]
        Ping_Avg_Time=Ping_Avg_Time/len(Ping_Node)
        pbar.update()


        pbar.set_description("resetting host names")
        Host_Node = nr.run(task=resettHostName)
        for x in Host_Node:
            Host_Conf_Avg_Time+=Host_Node[x].result[1]
            Host_Config_command_count+=Host_Node[x].result[0]
        tot+=Host_Config_command_count
        Host_Conf_Avg_Time=Host_Conf_Avg_Time/len(Host_Node)
        Host_Commands_per_sec=Host_Config_command_count/Host_Conf_Avg_Time
        nr = InitNornir(config_file="config.yaml") #re initialize the nornir object due to changes in hostname breaking the rest of the program if not reinitialized
        pbar.update()


        pbar.set_description("turning on cdp")
        CDP_Node = nr.run(task=TurnOnCDP)
        for x in CDP_Node:
            CDP_AvgTime+=CDP_Node[x].result[1]
            CDP_Command_Count+=CDP_Node[x].result[0]
            CDP_Average_Comand_Time+=CDP_Node[x].result[2]
        tot+=CDP_Command_Count
        CDP_AvgTime=CDP_AvgTime/len(CDP_Node)
        CDP_Average_Comand_Time=CDP_Average_Comand_Time/len(CDP_Node)
        CDP_Commands_Per_Sec=CDP_Command_Count/CDP_Average_Comand_Time
        pbar.update()


        pbar.set_description("configuring EIGRP underlay")
        EIGRP_Node = nr.run(task=MicroSegmenter,SegmentationIps="10.0",
            SpineHostName="spine", 
            LeafHostname="leaf", 
            IpDomainName="simon")
        for x in EIGRP_Node:
            EIGRP_Avg_Time+=EIGRP_Node[x].result[1]
            EIGRP_Command_Count+=EIGRP_Node[x].result[0]
            EIGRP_Average_Gather_Time=EIGRP_Node[x].result[2]
            EIGRP_AVG_Command_Time+=EIGRP_Node[x].result[3]
        tot+=EIGRP_Command_Count
        EIGRP_Avg_Time=EIGRP_Avg_Time/len(EIGRP_Node)
        EIGRP_AVG_Gather_Time=EIGRP_Average_Gather_Time/len(EIGRP_Node)
        EIGRP_AVG_Command_Time=EIGRP_AVG_Command_Time/len(EIGRP_Node)
        EIGRP_AVG_Commands_Per_Sec=EIGRP_Command_Count/EIGRP_AVG_Command_Time
        pbar.update()

        
        pbar.set_description("configging HSRP")
        HSRP_Node = nr.run(task=hsrpPair)
        for x in HSRP_Node:
            HSRP_AVG_Time+=HSRP_Node[x].result[1]
            HSRP_Command_Count+=HSRP_Node[x].result[0]
            Node_HSRP_Gather_Time=HSRP_Node[x].result[2]
            if Node_HSRP_Gather_Time != 0:
                HSRP_AVG_Gather_Time+=HSRP_Node[x].result[2]
                HSRP_Gather_Count+=1
            Node_HSRP_Command_Time=HSRP_Node[x].result[3]
            if Node_HSRP_Command_Time != 0:
                HSRP_Average_Comand_Time+=HSRP_Node[x].result[3]
                HSRP_Command_Time_counter+=1
        tot+=HSRP_Command_Count
        HSRP_AVG_Time=HSRP_AVG_Time/len(HSRP_Node)
        HSRP_AVG_Gather_Time=HSRP_AVG_Gather_Time/HSRP_Gather_Count
        HSRP_Average_Comand_Time=HSRP_Average_Comand_Time/HSRP_Command_Time_counter
        HSRPPScommands=HSRP_Command_Count/HSRP_Average_Comand_Time
        pbar.update()


        pbar.set_description("Setting up VPN Mesh")
        leafs = len(nr.inventory.children_of_group("leaf")) #this is the number of leafs in the network
        spines = len(nr.inventory.children_of_group("spine"))
        VPN_Node = nr.run(task=vpnMaker, NrOfLeafs=leafs, NrOfSpines=spines) #this is the vpn mesh function
        for x in VPN_Node:
            VPN_Command_Count+=VPN_Node[x].result[0]
            VPN_Avg_Time+=VPN_Node[x].result[1]
            Node_VPN_Gather_Time=VPN_Node[x].result[2]
            if Node_VPN_Gather_Time != 0:
                VPN_AVG_Gather_Time+=VPN_Node[x].result[2]
                VPN_Time_Gather_Count+=1
            Node_VPN_Command_Time=VPN_Node[x].result[3]
            if Node_VPN_Command_Time != 0:
                VPN_AVG_Command_Time+=VPN_Node[x].result[3]
                VPN_Command_Time_Counter+=1
        tot+=VPN_Command_Count
        VPN_Avg_Time=VPN_Avg_Time/len(VPN_Node)
        VPN_AVG_Gather_Time=VPN_AVG_Gather_Time/VPN_Time_Gather_Count
        VPN_AVG_Command_Time=VPN_AVG_Command_Time/VPN_Command_Time_Counter
        VPN_AVG_Commands_Per_Sec=VPN_Command_Count/VPN_AVG_Command_Time
        pbar.update()
        
        for y in VPN_Node["leaf1.cmh"].result[4]:
            print(y)
        pbar.update()


        #pbar.set_description("configuring edge leafs")
        #Edge_Nodes = nr.filter(F(groups__contains="edge")) #this is the nornir object with only the edge nodes
        #Edge_Node = Edge_Nodes.run(task=ConfigEdgeLeaf)
        #for x in Edge_Node:
        #    Edge_Command_Count+=Edge_Node[x].result[0]
        #    Edge_AVG_Time+=Edge_Node[x].result[1]
        #    Edge_AVG_Gather_Time+=Edge_Node[x].result[2]
        #    Edge_AVG_Command_Time+=Edge_Node[x].result[3]
        #tot+=Edge_Command_Count
        #Edge_AVG_Time=Edge_AVG_Time/len(Edge_Node)
        #Edge_AVG_Gather_Time=Edge_AVG_Gather_Time/len(Edge_Node)
        #Edge_AVG_Command_Time=Edge_AVG_Command_Time/len(Edge_Node)
        #Edge_AVG_Commands_Per_Sec=Edge_Command_Count/Edge_AVG_Command_Time
        #pbar.update()


        pbar.set_description("configuring DHCP Servers")
        DHCP_Nodes = nr.filter(F(groups__contains="leaf")) #this is the nornir object with only the edge nodes
        Pairs = int(len(nr.inventory.children_of_group("leaf"))/2) #this is the number of leafs
        DHCP_Pools = (subbnetter(nettwork=f"192.168.2.0",nettworkReq=[{"numberOfSubbnets":Pairs, "requiredHosts":255},]))
        DHCP_Node = DHCP_Nodes.run(task=AddDHCPPools, ipconfigs=DHCP_Pools)
        for x in DHCP_Node:
            DHCP_Command_Count+=DHCP_Node[x].result[0]
            DHCP_AVG_Time+=DHCP_Node[x].result[1]
            DHCP_AVG_Gather_Time+=DHCP_Node[x].result[2]
            DHCP_AVG_Command_Time+=DHCP_Node[x].result[3]
        tot+=DHCP_Command_Count
        DHCP_AVG_Time=DHCP_AVG_Time/len(DHCP_Node)
        DHCP_AVG_Gather_Time=DHCP_AVG_Gather_Time/len(DHCP_Node)
        DHCP_AVG_Command_Time=DHCP_AVG_Command_Time/len(DHCP_Node)
        DHCP_AVG_Commands_Per_Sec=DHCP_Command_Count/DHCP_AVG_Command_Time
        pbar.update()
#
        pbar.set_description("turning off cdp")
        nr.run(task=TurnOfCDP) #turn on CDP
        ofCdp_Node = nr.run(task=TurnOfCDP)
        for x in ofCdp_Node:
            tot+=ofCdp_Node[x].result[0]
            ofCdp_AvgTime+=ofCdp_Node[x].result[1]
        ofCdp_AvgTime=ofCdp_AvgTime/len(ofCdp_Node)
        pbar.update()


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
    try:
        print(f"\n\n\n\n\n\n\n\n\n\ntime spent on average pinging: {Ping_Avg_Time}")
        print(f"time spent configuring host information: {Host_Conf_Avg_Time}, sending a total command count of {Host_Config_command_count}, command PS count {Host_Commands_per_sec}")
        print(f"time spent configuring EIGRP: {EIGRP_Avg_Time}, sending a total command count of {EIGRP_Command_Count}, command PS count {EIGRP_AVG_Commands_Per_Sec} using a average of {EIGRP_AVG_Gather_Time} on gathering information")
        print(f"time spent configuring CDP: {CDP_AvgTime}, sending a total command count of {CDP_Command_Count}, command PS count {CDP_Commands_Per_Sec}")
        print(f"time spent configuring HSRP: {HSRP_AVG_Time}, sending a total command count of {HSRP_Command_Count}, command PS count {HSRPPScommands}")
        print(f"time spent configuring VPN Mesh: {VPN_Avg_Time}, sending a total command count of {VPN_Command_Count}, command PS count {VPN_AVG_Commands_Per_Sec}")
        #print(f"time spent configuring edge leafs: {Edge_AVG_Time}, sending a total command count of {Edge_Command_Count}, command PS count {Edge_AVG_Commands_Per_Sec}")
        print(f"time spent configuring DHCP: {DHCP_AVG_Time}, sending a total command count of {DHCP_Command_Count}, command PS count {DHCP_AVG_Commands_Per_Sec}")
        print(f"time spent turning off cdp: {ofCdp_AvgTime}")
        print(f"total command PS: {(Host_Commands_per_sec+EIGRP_AVG_Commands_Per_Sec+CDP_Commands_Per_Sec+HSRPPScommands+VPN_AVG_Commands_Per_Sec)/6}") #!add Edge_AVG_Commands_Per_Sec
        print(f"total commands sent: {tot}")
    except:
        print("error")



main() #run the main function


print(f"the script took {time.time()-startTime} seconds") #prints how long the script took to run
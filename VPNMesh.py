from Subbnetter import subbnetter
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result

#TODO
#?HSRP tunnel from to?

#?MAKE A VLAN FROMTO TUNNEL???

#find out what ip to asign to the tunnel interface(s?)
#? take the ip in the tunnel vlan and assign the ip that matches the leaf number to the tunnel interface(s?)

#figgure out the from to ip adresses for the tunnel
#? take interface info and use that as the from ip adress for the tunnel

#find out if i am going to use static or dynamic routing in the tunnel
#?try to change the underlay to use eigrp and use ospf for the tunnel routing or if i want to be lazy i can just use static routing

#? add vlan and tunel to ospf

#set up the routes

#need NrOfSpines*NrOfLeafs tunel interfaces
#loop on the spines
#loop on the leafs

#make one subbnet per leaf 

#base the tunnel ip on the leaf id

#if leafnr of the one you are on is higher then the one you are trying to connect to choose the lower one
#just brute force it to begin with

def vpnMaker(node, NrOfLeafs, NrOfSpines):
    tunnelLan=[]
    for x in range(0,NrOfLeafs): #not very modular and not very efficient in adition not very elegant either
        tunnelLan.append(subbnetter(nettwork=f"10.3.{x}.0",nettworkReq=[{"numberOfSubbnets":NrOfLeafs, "requiredHosts":2},]))

    subbnetList=[]
    for x in range(0,9): #makes 10 subbnets
        subbnetList.append(subbnetter(nettwork=f"10.0.{x}.0",nettworkReq=[{"numberOfSubbnets":64, "requiredHosts":2},])) #makes 64 subbnets with 2 hosts each


    node.host["run"] = node.run(task=netmiko_send_command, command_string=("sh run"), enable=True).result #this is the running config
    if "hostname leaf" in node.host["run"]:
        locationOfQuote=node.host["run"].find(f"hostname leaf")
        LeafNr=int(node.host["run"][locationOfQuote+13:locationOfQuote+15].replace(" ","").replace("\n",""))-1

        commandList=[f"router ospf 1",f"exit",f"int vl 1", f"ip os 1 a 0", f"exit"]

        counter=0
        for i in range(0, NrOfSpines):
            for j in range(0, NrOfLeafs):
                if subbnetList[i][LeafNr] != subbnetList[i][j]:
                    FromIp = (f"{subbnetList[i][LeafNr]['subbnetID'].split('.')[0]}.{subbnetList[i][LeafNr]['subbnetID'].split('.')[1]}.{subbnetList[i][LeafNr]['subbnetID'].split('.')[2]}.{int(subbnetList[i][LeafNr]['subbnetID'].split('.')[3])+2}")
                    toIp = (f"{subbnetList[i][j]['subbnetID'].split('.')[0]}.{subbnetList[i][j]['subbnetID'].split('.')[1]}.{subbnetList[i][j]['subbnetID'].split('.')[2]}.{int(subbnetList[i][j]['subbnetID'].split('.')[3])+2}")
                    tunnelIp = (f"{tunnelLan[i][j]['subbnetID'].split('.')[0]}.{tunnelLan[i][j]['subbnetID'].split('.')[1]}.{tunnelLan[i][j]['subbnetID'].split('.')[2]}.{int(tunnelLan[i][j]['subbnetID'].split('.')[3])+1}")

                    commandList.append(f"interface tunnel {counter}")
                    commandList.append(f"tunnel source {FromIp}")
                    commandList.append(f"tunnel destination {toIp}")
                    commandList.append(f"ip address {tunnelIp} {tunnelLan[i][j]['mask']}")
                    commandList.append(f"ip ospf 1 a 0")
                    commandList.append(f"exit")

                    print(f"ip address {tunnelIp} {tunnelLan[i][j]['mask']} {LeafNr+1} from {FromIp} to {toIp}")
                    
                counter+=1


        print("\n")
        #print(LeafNr)
        #for x in commandList:
        #    print(x)

        #print(commandList)
        #test = node.run(task=netmiko_send_config, config_commands=commandList)
        #print_result(test)

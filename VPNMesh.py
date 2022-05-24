from cmath import nan
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
#3 dim list
#1 dim switch
#2 dim subbnet
#3 dim...
#4 ???

def vpnMaker(node, NrOfLeafs, NrOfSpines):
    tunnelLan=[]
    for x in range(0,NrOfLeafs): #not very modular and not very efficient in adition not very elegant either
        tunnelLan.append(subbnetter(nettwork=f"10.3.{x}.0",nettworkReq=[{"numberOfSubbnets":NrOfLeafs, "requiredHosts":2},]))

    iplist=[
            [[nan,"0.1","0.5","0.9","0.13","0.17"]],#[0,0,0,0,0,0],[0,0,0,0,0,0]],
            [["0.2",nan,"0.21","0.25","0.29","0.33"]],#[0,0,0,0,0,0],[0,0,0,0,0,0]],
            [["0.6","0.22",nan,"0.37","0.41","0.45"]],#[0,0,0,0,0,0],[0,0,0,0,0,0]],
            [["0.10","0.26","0.38",nan,"0.49","0.53"]],#[0,0,0,0,0,0],[0,0,0,0,0,0]],
            [["0.14","0.30","0.42","0.50",nan,"0.57"]],#[0,0,0,0,0,0],[0,0,0,0,0,0]],
            [["0.18","0.34","0.46","0.54","0.58",nan]],#[0,0,0,0,0,0],[0,0,0,0,0,0]],
            ]


    NewIpList = []
    for Dim1 in range(0,NrOfLeafs):
        NewIpList.append([])
        for Dim2 in range(0,NrOfSpines):
            NewIpList[Dim1].append([])

            Horisontal=False
            for Dim3 in range(0,NrOfLeafs):
                if Dim3 == Dim1:
                    NewIpList[Dim1][Dim2].append("nan")
                    Horisontal=True
                else:

                    if Dim1 == 0:
                        if NewIpList[Dim1][Dim2][-1]=="nan":
                            NewIpList[Dim1][Dim2].append(f"{Dim2}.1")
                        else:
                            prev = NewIpList[Dim1][Dim2][-1]
                            NewIpList[Dim1][Dim2].append(f"{prev.split('.')[0]}.{int(prev.split('.')[1])+4}")
                    
                    else:
                        if Horisontal:
                            if NewIpList[Dim1][Dim2][-1]=="nan":
                                NewIpList[Dim1][Dim2].append(f"{NewIpList[Dim1-1][Dim2][-1].split('.')[0]}.{int(NewIpList[Dim1-1][Dim2][-1].split('.')[1])+4}")
                            else:
                                NewIpList[Dim1][Dim2].append(NewIpList[Dim1][Dim2][-1].split('.')[0]+"."+str(int(NewIpList[Dim1][Dim2][-1].split('.')[1])+4))

                        else:
                            NewIpList[Dim1][Dim2].append(NewIpList[Dim3][Dim2][Dim1].split('.')[0]+"."+str(int(NewIpList[Dim3][Dim2][Dim1].split('.')[1])+1))
    #print(NewIpList)
    #print("\n")
    #for x in NewIpList:
    #    print(x)


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
                    
                    tunnelIp = f"10.3.{NewIpList[LeafNr][i][j]}"

                    commandList.append(f"interface tunnel {counter}")
                    commandList.append(f"tunnel source {FromIp}")
                    commandList.append(f"tunnel destination {toIp}")
                    commandList.append(f"ip address {tunnelIp} {tunnelLan[i][j]['mask']}")
                    commandList.append(f"ip ospf 1 a 0")
                    commandList.append(f"exit")

                    print(f"ip address {tunnelIp} {tunnelLan[i][j]['mask']} {LeafNr+1} from {FromIp} to {toIp} {counter} {i} {j}")

                counter+=1


        print("\n")
        #print(LeafNr)
        #for x in commandList:
        #    print(x)

        print(commandList)
        test = node.run(task=netmiko_send_config, config_commands=commandList)
        print_result(test)

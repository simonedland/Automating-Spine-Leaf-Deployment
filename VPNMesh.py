from Subbnetter import subbnetter
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from tqdm import tqdm


def vpnMaker(node, NrOfLeafs, NrOfSpines):
    
    pbar = tqdm(total=3)
    pbar.colour = "yellow"

    tunnelLan=[]
    for x in range(0,NrOfLeafs): #not very modular and not very efficient in adition not very elegant either
        tunnelLan.append(subbnetter(nettwork=f"10.3.{x}.0",nettworkReq=[{"numberOfSubbnets":NrOfLeafs, "requiredHosts":2},]))


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


    subbnetList=[]
    for x in range(0,9): #makes 10 subbnets
        subbnetList.append(subbnetter(nettwork=f"10.0.{x}.0",nettworkReq=[{"numberOfSubbnets":64, "requiredHosts":2},])) #makes 64 subbnets with 2 hosts each

    pbar.update()
    pbar.set_description(f"{node.host} gathering info")

    node.host["run"] = node.run(task=netmiko_send_command, command_string=("sh run"), enable=True).result #this is the running config

    pbar.update()
    pbar.set_description(f"{node.host} sending config")

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

                counter+=1

        node.run(task=netmiko_send_config, config_commands=commandList)
        

        pbar.colour = "green"
        pbar.update()
        pbar.set_description(f"{node.host} done")

    else:
        pbar.colour = "green"
        pbar.update()
        pbar.set_description(f"{node.host} not a leaf")
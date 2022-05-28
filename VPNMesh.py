from Subbnetter import subbnetter
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from tqdm import tqdm
import time

def vpnMaker(node, NrOfLeafs, NrOfSpines):
    
    startTime = time.time()

    pbar = tqdm(total=3)
    pbar.colour = "yellow"

    tunnelLan=[]
    for x in range(0,NrOfLeafs): #not very modular and not very efficient in adition not very elegant either
        tunnelLan.append(subbnetter(nettwork=f"10.3.{x}.0",nettworkReq=[{"numberOfSubbnets":NrOfLeafs, "requiredHosts":2},]))

    #!WARNING THIS IS TRASH CODE BUT IT WORKS
    #!EXPLAIN HOW THE LISTS ARE CONNECTED IN THE PAPER
    #it constructs the tunnelLan list whewre the first dimention is leafs
    #and the second dimention is the subnets related to the ip connected to the spines
    #and the third dimention is the hosts in the subnet meaning it has the same amount that there is leafs
    NewIpList = []
    for Dim1 in range(0,NrOfLeafs): #this makes the ip list for the leafs
        NewIpList.append([]) #append a new list to the list
        for Dim2 in range(0,NrOfSpines): #makes another dimension for the ip list that is asosiated with the number of spines
            NewIpList[Dim1].append([]) #append a new list to the list
            Horisontal=False #this is the horizontal flag that changes the ip grid to use new ips when passing trough the tunnel that should have pointed to ti self
            for Dim3 in range(0,NrOfLeafs): #adds the last dimension to the ip list that is asosiated with the number of leafs
                if Dim3 == Dim1: #if the ip is on the same row as the leaf meaning it is on the same tunnel (pointing to self)
                    NewIpList[Dim1][Dim2].append("nan") #adds a nan to the ip list
                    Horisontal=True #sets the horizontal flag to true
                else: #if the ip is not on the same row as the leaf meaning it is on a different tunnel (pointing to another leaf)
                    if Dim1 == 0: #if the ip is on the first row meaning it is on the first leaf
                        if NewIpList[Dim1][Dim2][-1]=="nan": #if the last ip is a nan meaning that it is the beginning of the list
                            NewIpList[Dim1][Dim2].append(f"{Dim2}.1") #adds the ip to the list
                        else: #if the last ip is not a nan meaning that it is not the beginning of the list
                            prev = NewIpList[Dim1][Dim2][-1] #sets the prev variable to the last ip in the list
                            NewIpList[Dim1][Dim2].append(f"{prev.split('.')[0]}.{int(prev.split('.')[1])+4}") #adds the ip to the list and adds 4 to the ip
                    else: #if the ip is not on the first row meaning it is on a row that is not the first leaf
                        if Horisontal: #if it needs to create new ips bechause it passed itself
                            if NewIpList[Dim1][Dim2][-1]=="nan": #it it just passed
                                NewIpList[Dim1][Dim2].append(f"{NewIpList[Dim1-1][Dim2][-1].split('.')[0]}.{int(NewIpList[Dim1-1][Dim2][-1].split('.')[1])+4}") #takes the last ip of the previous leaf and adds 4 to it
                            else: #if it is not just passed
                                NewIpList[Dim1][Dim2].append(NewIpList[Dim1][Dim2][-1].split('.')[0]+"."+str(int(NewIpList[Dim1][Dim2][-1].split('.')[1])+4)) #adds 4 to the last ip of the list
                        else: #if it has another leaf to connect to
                            NewIpList[Dim1][Dim2].append(NewIpList[Dim3][Dim2][Dim1].split('.')[0]+"."+str(int(NewIpList[Dim3][Dim2][Dim1].split('.')[1])+1)) #adds 1 to the last ip of the list choosinga higher ip in the microsegment


    for i in NewIpList:
        print(i)
        
    subbnetList=[]
    for x in range(0,9): #makes 10 subbnets
        subbnetList.append(subbnetter(nettwork=f"10.0.{x}.0",nettworkReq=[{"numberOfSubbnets":64, "requiredHosts":2},])) #makes 64 subbnets with 2 hosts each

    pbar.update()
    pbar.set_description(f"{node.host} gathering info")

    GatherTimeStart = time.time()
    node.host["run"] = node.run(task=netmiko_send_command, command_string=("sh run"), enable=True).result #this is the running config
    GatherTimeEnd = time.time()

    pbar.update()
    pbar.set_description(f"{node.host} sending config")

    if "hostname leaf" in node.host["run"]: #if the host is a leaf
        locationOfQuote=node.host["run"].find(f"hostname leaf") #finds the location of the quote
        LeafNr=int(node.host["run"][locationOfQuote+13:locationOfQuote+15].replace(" ","").replace("\n",""))-1 #finds the leaf number and takes -1 bechause we are computers

        commandList=[f"router ospf 1",f"exit",f"int vl 1", f"ip os 1 a 0", f"exit"] #makes the command list with the initial commands
        counter=0 #sets the counter to 0

        for i in range(0, NrOfSpines): #for every spine
            for j in range(0, NrOfLeafs): #for every leaf
                if subbnetList[i][LeafNr] != subbnetList[i][j]: #if the leaf is not in the same subnet as itself (prevents making making a tunnel to self)

                    FromIp = (f"{subbnetList[i][LeafNr]['subbnetID'].split('.')[0]}.{subbnetList[i][LeafNr]['subbnetID'].split('.')[1]}.{subbnetList[i][LeafNr]['subbnetID'].split('.')[2]}.{int(subbnetList[i][LeafNr]['subbnetID'].split('.')[3])+2}") #sets the ip of the leaf that is the source of the tunnel by using the same script that makes the EIGRP fabric
                    toIp = (f"{subbnetList[i][j]['subbnetID'].split('.')[0]}.{subbnetList[i][j]['subbnetID'].split('.')[1]}.{subbnetList[i][j]['subbnetID'].split('.')[2]}.{int(subbnetList[i][j]['subbnetID'].split('.')[3])+2}") #sets the ip of the leaf that is the destination of the tunnel
                    
                    tunnelIp = f"10.3.{NewIpList[LeafNr][i][j]}" #sets the ip of the tunnel #!THIS WAS PAIN IN THE ASS TO FIND OUT HOW TO DO. ╰(*°▽°*)╯

                    commandList.append(f"interface tunnel {counter}") #adds the command to the command list
                    commandList.append(f"tunnel source {FromIp}")
                    commandList.append(f"tunnel destination {toIp}")
                    commandList.append(f"ip address {tunnelIp} {tunnelLan[i][j]['mask']}")
                    commandList.append(f"ip ospf 1 a 0")
                    commandList.append(f"exit")

                counter+=1 #adds 1 to the counter

        CommandStartTime=time.time() #sets the time when the command starts
        node.run(task=netmiko_send_config, config_commands=commandList) #sends the config to the leaf
        CommandEndTime=time.time() #sets the time when the command ends
        

        pbar.colour = "green"
        pbar.update()
        pbar.set_description(f"{node.host} done")

    else:
        commandList=[]
        pbar.colour = "green"
        pbar.update()
        pbar.set_description(f"{node.host} not a leaf")
        GatherTimeEnd=0
        GatherTimeStart=0
        CommandEndTime=0
        CommandStartTime=0
        


    endTime = time.time()
    return len(commandList)+1, endTime-startTime, GatherTimeEnd-GatherTimeStart, CommandEndTime-CommandStartTime
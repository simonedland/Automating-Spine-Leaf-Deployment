#tunnelLan=[]
NrOfSpines=1
NrOfLeafs=66
scale=4
Oct3Offset=0

from Subbnetter import subbnetter

#for x in range(0,NrOfSpines): #not very modular and not very efficient in adition not very elegant either
#    tunnelLan.append(subbnetter(nettwork=f"10.3.{x*scale}.0",nettworkReq=[{"numberOfSubbnets":NrOfLeafs, "requiredHosts":2},]))

#!WARNING THIS IS TRASH CODE BUT IT WORKS
#!EXPLAIN HOW THE LISTS ARE CONNECTED IN THE PAPER
#it constructs the tunnelLan list whewre the first dimention is leafs
#and the second dimention is the subnets related to the ip connected to the spines
#and the third dimention is the hosts in the subnet meaning it has the same amount that there is leafs

iteration=0

NewIpList = []
for Dim1 in range(0,NrOfLeafs): #this makes the ip list for the leafs
    NewIpList.append([]) #append a new list to the list
    for Dim2 in range(0,NrOfSpines): #makes another dimension for the ip list that is asosiated with the number of spines
        NewIpList[Dim1].append([]) #append a new list to the list
        Horisontal=False #this is the horizontal flag that changes the ip grid to use new ips when passing trough the tunnel that should have pointed to ti self
        for Dim3 in range(0,NrOfLeafs): #adds the last dimension to the ip list that is asosiated with the number of leafs
            if Dim3 == Dim1: #if the ip is on the same row as the leaf meaning it is on the same tunnel (pointing to self)
                NewIpList[Dim1][Dim2].append("nan") #adds a nan to the ip list
                
                iteration+=1
                print(iteration)
                for x in NewIpList:
                    print(x)
                print("\n")

                Horisontal=True #sets the horizontal flag to true
            else: #if the ip is not on the same row as the leaf meaning it is on a different tunnel (pointing to another leaf)
                if Dim1 == 0: #if the ip is on the first row meaning it is on the first leaf
                    if NewIpList[Dim1][Dim2][-1]=="nan": #if the last ip is a nan meaning that it is the beginning of the list
                        NewIpList[Dim1][Dim2].append(f"{Dim2*scale+Oct3Offset}.1") #adds the ip to the list

                        iteration+=1
                        print(iteration)
                        for x in NewIpList:
                            print(x)
                        print("\n")

                    else: #if the last ip is not a nan meaning that it is not the beginning of the list
                        prev = NewIpList[Dim1][Dim2][-1] #sets the prev variable to the last ip in the list
                        if int(prev.split('.')[1]) == 253: #if the last ip is the last ip in the list
                            Oct3Offset+=1
                            NewIpList[Dim1][Dim2].append(str(f"{int(prev.split('.')[0])+Oct3Offset}.1"))
                        else:
                            NewIpList[Dim1][Dim2].append(f"{prev.split('.')[0]}.{int(prev.split('.')[1])+4}") #adds the ip to the list and adds 4 to the ip

                        iteration+=1
                        print(iteration)
                        for x in NewIpList:
                            print(x)
                        print("\n")

                else: #if the ip is not on the first row meaning it is on a row that is not the first leaf
                    if Horisontal: #if it needs to create new ips bechause it passed itself
                        if NewIpList[Dim1][Dim2][-1]=="nan": #it it just passed
                            if int(NewIpList[Dim1-1][Dim2][-1].split('.')[1]) == 253: #if the ip is the last ip in the row
                                Oct3Offset+=1
                                NewIpList[Dim1][Dim2].append(f"{int(NewIpList[0][0][1].split('.')[0])+Oct3Offset}.1")
                            #print(NewIpList[Dim1-1][Dim2][-1].split('.')[1])
                            else:
                                NewIpList[Dim1][Dim2].append(f"{NewIpList[Dim1-1][Dim2][-1].split('.')[0]}.{int(NewIpList[Dim1-1][Dim2][-1].split('.')[1])+4}") #takes the last ip of the previous leaf and adds 4 to it
                            
                            iteration+=1
                            print(iteration)
                            for x in NewIpList:
                                print(x)
                            print("\n")

                        else: #if it is not just passed
                            print(int(NewIpList[Dim1][Dim2][-1].split('.')[1])+4)

                            if int(NewIpList[Dim1][Dim2][-1].split('.')[1]) == 253:
                                Oct3Offset+=1
                                NewIpList[Dim1][Dim2].append(str(int(NewIpList[1][0][-1].split('.')[0])+Oct3Offset)+"."+str("1")) #adds 4 to the last ip of the list
                            else:
                                NewIpList[Dim1][Dim2].append(str(int(NewIpList[Dim1][Dim2][-1].split('.')[0]))+"."+str(int(NewIpList[Dim1][Dim2][-1].split('.')[1])+4)) #adds 4 to the last ip of the list
                            
                            iteration+=1
                            print(iteration)
                            for x in NewIpList:
                                print(x)
                            print("\n")
                            
                    else: #if it has another leaf to connect to
                        NewIpList[Dim1][Dim2].append(NewIpList[Dim3][Dim2][Dim1].split('.')[0]+"."+str(int(NewIpList[Dim3][Dim2][Dim1].split('.')[1])+1)) #adds 1 to the last ip of the list choosinga higher ip in the microsegment
                        
                        iteration+=1
                        print(iteration)
                        for x in NewIpList:
                            print(x)
                        print("\n")
                        
#for x in tunnelLan:
#    for y in x:
#        print(y)

for x in NewIpList:
    print(x)
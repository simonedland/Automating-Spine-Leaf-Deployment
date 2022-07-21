def subbnetter(nettwork, nettworkReq):
    
    nettworkReq = sorted(nettworkReq, 
                        key=lambda d:d["requiredHosts"],
                        reverse = True)
    #sorts by using the required hosts as the key

    y=1
    octetValueList=[] #list of octet values
    for x in range(32):
        octetValueList.append(y) #adds the values to the list
        y=y*2 #makes the binary values

    #takes the nettworkreq and constructs subbnets based on the number of subbnets and the required hosts
    subbnets=[]
    for x in nettworkReq:
        for y in range(x["numberOfSubbnets"]):

            #finds the minimum host ips to use per subnet
            host_bit_value=0
            i=0
            while host_bit_value-2<x["requiredHosts"]: #subtracts 2 bechause the avaidable number of ips is difrent from the total number of ips
                host_bit_value=octetValueList[i]
                i+=1
            

            #find the sbnetID
            host_bit_length=len(bin(host_bit_value)[2:])

            if host_bit_length<=8:
                print(nettwork)
                octet_bits=bin(int(nettwork.split(".")[3]))[2:]
                new_octet_bits=octet_bits[:-host_bit_length+1]+"0"*(host_bit_length-1) #cleans the bits up for the subbnet by replacing anny 1 where there should be 0
                new_octet_int=int(f"{new_octet_bits}",2)
                if host_bit_value+new_octet_int==256:
                    if int(nettwork.split('.')[2])+1==256:
                        if int(nettwork.split('.')[1])+1==256:
                            next_nettwork=f"{int(nettwork.split('.')[0])+1}.0.0.0"
                        else:
                            next_nettwork=f"{nettwork.split('.')[0]}.{int(nettwork.split('.')[1])+1}.0.0"
                    else:
                        next_nettwork=f"{nettwork.split('.')[0]}.{nettwork.split('.')[1]}.{int(nettwork.split('.')[2])+1}.{0}"
                    new_octet_int=0
                else:
                    next_nettwork=f"{nettwork.split('.')[0]}.{nettwork.split('.')[1]}.{nettwork.split('.')[2]}.{new_octet_int+host_bit_value}"
                nettwork=next_nettwork
                print(nettwork)


            elif host_bit_length>8 and host_bit_length<=16:
                print("more than 8")
                print(nettwork.split(".")[2])

            elif host_bit_length>16 and host_bit_length<=24:
                print("more than 16")
                print(nettwork.split(".")[1])

            elif host_bit_length>24 and host_bit_length<=32:
                print("more than 24")
                print(nettwork.split(".")[0])
            

            print("\n")
            #do the subbnetting

            #make that the new subbnet id


    print(bin(25)[2:])
    print(nettworkReq)
    
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
            
            print(nettwork)

            #finds the minimum host ips to use per subnet
            host_bit_value=0
            i=0
            while host_bit_value-2<x["requiredHosts"]: #subtracts 2 bechause the avaidable number of ips is difrent from the total number of ips
                host_bit_value=octetValueList[i]
                i+=1
            
            #find the sbnetID
            host_bit_length=len(bin(host_bit_value)[2:])

            if host_bit_length<=8:
                octet_bits=bin(int(nettwork.split(".")[3]))[2:]
                new_octet_bits=octet_bits[:-host_bit_length+1]+"0"*(host_bit_length-1)
                new_octet_int=int(f"{new_octet_bits}",2)
                if new_octet_int+host_bit_value>=256: #if octet four overflows
                    if int(nettwork.split(".")[2])+1>=256:
                        if int(nettwork.split(".")[1])+1>=256:
                            new_nettwork_ID=f"{int(nettwork.split('.')[0])+1}.0.0.0"
                        else:
                            new_nettwork_ID=f"{nettwork.split('.')[0]}.{int(nettwork.split('.')[1])+1}.0.0"
                    else:
                        new_nettwork_ID=f"{nettwork.split('.')[0]}.{nettwork.split('.')[1]}.{int(nettwork.split('.')[2])+1}.0"
                else:
                    new_nettwork_ID=f"{nettwork.split('.')[0]}.{nettwork.split('.')[1]}.{nettwork.split('.')[2]}.{new_octet_int+host_bit_value}"
                nettwork=f"{nettwork.split('.')[0]}.{nettwork.split('.')[1]}.{nettwork.split('.')[2]}.{new_octet_int}"

            elif host_bit_length>8 and host_bit_length<=16:
                octet_bits=bin(int(nettwork.split(".")[2]))[2:]
                new_octet_bits=octet_bits[:(9-host_bit_length)]+"0"*(host_bit_length-9)
                if new_octet_bits: #prevents there from beeing an error if you only add one to the octet
                    new_octet_int=int(f"{new_octet_bits}",2)
                else:
                    new_octet_int=int(f"{octet_bits}",2)
                if (host_bit_value/256)+new_octet_int==256: #if octet three overflows
                    if int(nettwork.split('.')[1])+1==256:
                        new_nettwork_ID=f"{int(nettwork.split('.')[0])+1}.0.0.0"
                    else:
                        new_nettwork_ID=f"{nettwork.split('.')[0]}.{int(nettwork.split('.')[1])+1}.0.0"
                else:
                    new_nettwork_ID=f"{nettwork.split('.')[0]}.{nettwork.split('.')[1]}.{new_octet_int+(int(host_bit_value/256))}.0"
                nettwork=f"{nettwork.split('.')[0]}.{nettwork.split('.')[1]}.{new_octet_int}.0"

            elif host_bit_length>16 and host_bit_length<=24:
                octet_bits=bin(int(nettwork.split(".")[1]))[2:]
                new_octet_bits=octet_bits[:(17-host_bit_length)]+"0"*(host_bit_length-17)
                if new_octet_bits: #prevents there from beeing an error if you only add one to the octet
                    new_octet_int=int(f"{new_octet_bits}",2)
                else:
                    new_octet_int=int(f"{octet_bits}",2)
                if (host_bit_value/256/256)+new_octet_int==256: #if octet two overflows
                    nettwork=f"{int(nettwork.split('.')[0])}.{new_octet_int}.0.0"
                    new_nettwork_ID=f"{int(nettwork.split('.')[0])+1}.0.0.0"
                else:
                    new_nettwork_ID=f"{nettwork.split('.')[0]}.{new_octet_int+(int(host_bit_value/(256*256)))}.0.0"
                nettwork=f"{nettwork.split('.')[0]}.{new_octet_int}.0.0"

            elif host_bit_length>24 and host_bit_length<=32:
                octet_bits=bin(int(nettwork.split(".")[0]))[2:]
                new_octet_bits=octet_bits[:(25-host_bit_length)]+"0"*(host_bit_length-25)
                if new_octet_bits: #prevents there from beeing an error if you only add one to the octet
                    new_octet_int=int(f"{new_octet_bits}",2)
                else:
                    new_octet_int=int(f"{octet_bits}",2)
                nettwork=f"{new_octet_int}.0.0.0"
                new_nettwork_ID=f"{new_octet_int+(int(host_bit_value/(256*256*256)))}.0.0.0"



            subbnetBittList=[0,128,192,224,240,248,252,254,255] #list of subbnet bits
            octet1,octet2,octet3,octet4=0,0,0,0 #octet values
            maskList=[0,0,0,0] #list of mask values
            for i in range(33-host_bit_length): #for each bit
                if maskList[0]==255: #if the mask is 255
                    if maskList[1]==255: #if the mask is 255
                        if maskList[2]==255: #if the mask is 255
                            if maskList[3]==255: #if the mask is 255
                                pass
                            else: #if the mask is not 255
                                octet4+=1 #adds 1 to the mask
                                maskList[3]=subbnetBittList[octet4] #sets the mask to the subbnet bit
                        else:
                            octet3+=1
                            maskList[2]=subbnetBittList[octet3]
                    else:
                        octet2+=1
                        maskList[1]=subbnetBittList[octet2]
                else:
                    octet1+=1
                    maskList[0]=subbnetBittList[octet1]
            mask=f"{maskList[0]}.{maskList[1]}.{maskList[2]}.{maskList[3]}" #sets the mask

            networkList.append({"subbnetID":subbnetID, "broadcast":broadcast, "mask":mask, "nrOfHostsAvaidable":f"{octetvale}"})
            print(nettwork)
            nettwork=new_nettwork_ID
            
            print(new_nettwork_ID, mask)
            print("\n")
            

    print(bin(25)[2:])
    print(nettworkReq)
    
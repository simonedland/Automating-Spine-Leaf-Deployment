def subbnetter(nettwork, nettworkReq):
    
    nettworkReq = sorted(nettworkReq, key=lambda d:d["requiredHosts"], reverse = True)
    #sorts by using the required hosts as the key

    octetValueList=[] #list of octet values
    for x in range(32):
        octetValueList.append(y) #adds the values to the list
        y=y*2 #makes the binary values


    #takes the nettworkreq and constructs subbnets based on the number of subbnets and the required hosts
    subbnets=[]
    for x in nettworkReq:
        for y in range(x["numberOfSubbnets"]):
            

            print(y)


    print(bin(25)[2:])
    print(nettworkReq)
    
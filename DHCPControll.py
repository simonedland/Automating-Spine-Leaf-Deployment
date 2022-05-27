from nornir_netmiko.tasks import netmiko_send_config

def AddDHCPPools(node, ipconfigs, gateway="first"):
    """makes the command list of adding the dhcp pools with netmiko
    normaly used with my subbnetter script
    requires a list of dictionaries with the keys: subbnetID, broadcast and mask
    this also points the dns to 8.8.8.8
    the gateway is placed in the first avadable adress this can be spesified by setting the gateway="last" when caling
    """
    
    #EXAMPLE OF HOW TO CALL THIS FUNCTION
    #subbnets = subbnetter(nettwork=f"10.1.0.0",
    #        nettworkReq=[
    #        {"numberOfSubbnets":64, "requiredHosts":2},
    #        ])
    
    #nr.run(task=AddDHCPPools, ipconfigs=subbnets)


    #todo
    #add dns option
    #add the option to reserve adresses

    counter=0
    commandlist=[]
    for ips in ipconfigs:
        
        if gateway =="first":
            gateway=f"{str(ips['subbnetID']).split('.')[0]}.{str(ips['subbnetID']).split('.')[1]}.{str(ips['subbnetID']).split('.')[2]}.{int(str(ips['subbnetID']).split('.')[3])+1}"
        elif gateway =="last":
            gateway=f"{str(ips['broadcast']).split('.')[0]}.{str(ips['broadcast']).split('.')[1]}.{str(ips['broadcast']).split('.')[2]}.{int(str(ips['broadcast']).split('.')[3])-1}"
        else:
            gateway=f"{str(ips['subbnetID']).split('.')[0]}.{str(ips['subbnetID']).split('.')[1]}.{str(ips['subbnetID']).split('.')[2]}.{int(str(ips['subbnetID']).split('.')[3])+1}"

        commandlist.append(f"ip dhcp pool Pool{counter}")
        commandlist.append(f"network {ips['subbnetID']} {ips['mask']}")
        commandlist.append(f"dns-server 8.8.8.8")
        commandlist.append(f"default-router {gateway}")
        commandlist.append(f"exit")

        counter+=1

    print(commandlist)
    #node.run(task=netmiko_send_config, config_commands=commandlist)
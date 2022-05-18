#TODO
#find out what ip to asign to the tunnel interface(s?)
#? take the ip in the tunnel vlan and assign the ip that matches the leaf number to the tunnel interface(s?)

#figgure out the from to ip adresses for the tunnel
#? take interface info and use that as the from ip adress for the tunnel

#find out if i am going to use static or dynamic routing in the tunnel
#?try to change the underlay to use eigrp and use ospf for the tunnel routing or if i want to be lazy i can just use static routing

#set up the routes

def vpnMaker(node, NrOfLeafs):
    print(NrOfLeafs)
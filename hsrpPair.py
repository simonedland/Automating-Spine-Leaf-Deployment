#todo:
#find out what ip it should use (can probably use some code from microsegment.py and/or subbnetter.py and also base the desision of host.yaml group name)
#find out what interface to apply the ip to (here too)
#find out what vlan to use (security)
#implement preemptive on BOTH sides
#implement priority decrementing based on interfaces
#use CDP to find out what interfaces are connected to what
#ignore STP due to the switches only beeing connected to one another unless the server is switched this means that i can use portfast
#trunking the interfaces
#some of the information might be usefull to save for the tunneling but then again i want to make it modular to prevent having to change the code in difrent places then where the issue is

from pingTest import ping

def hsrpPair(node):
    node.run(task=ping)


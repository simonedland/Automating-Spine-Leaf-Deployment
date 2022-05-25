
#a function that should configgure the edge leafs to be the default gateway for the WAN
#this function should also configgure the routers to be the default gateway for the WAN

#? to match the ip range of the connected leafs to the connected edge routers i can say that it is connected to leaf group X
#config the nat translation for the edge routers

from microsegmenter import MicroSegmenter

def ConfigEdgeLeaf(node):
    #this is the configuration of the edge leafs
    print("test")
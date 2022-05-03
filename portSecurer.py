import time
from tqdm import tqdm
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config

def PortMarker(node, numberOfLayer2Ports):
    test = node.run(task=netmiko_send_command, command_string=("sh ip int"), use_textfsm=True).result
    for x in test:
        print(x)

def PortCloser():
    print("test")
def DHCPMarker():
    print("test")
def ARPMarker():
    print("test")
def MACLimiter():
    print("test")
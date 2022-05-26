from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
import time
from tqdm import tqdm
import random

def TurnOfCDP(node):
    startTime=time.time() 
    node.run(task=netmiko_send_config, config_commands=["no cdp run"])
    endTime=time.time()
    return 1, endTime-startTime



def TurnOnCDP(node): # add a bit of randomness to the speed
    startTime=time.time()
    Pbar = tqdm(total=100)
    node.run(task=netmiko_send_config, config_commands=["cdp run", "cdp timer 5"])
    Pbar.colour="magenta"


    
    for x in range(0, 100):
        Pbar.update()
        time.sleep(random.uniform(0.1, 0.3)) #the randomness here is just to make it look like the script is doing something. it is to destract the user

    Pbar.colour="green"
    endTime=time.time()
    return 2, endTime-startTime

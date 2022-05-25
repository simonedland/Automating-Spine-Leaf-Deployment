from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
import time
from tqdm import tqdm
import random

def TurnOfCDP(node):
    node.run(task=netmiko_send_config, config_commands=["no cdp run"])

def TurnOnCDP(node): # add a bit of randomness to the speed
    Pbar = tqdm(total=150)
    node.run(task=netmiko_send_config, config_commands=["cdp run", "cdp timer 5"])
    Pbar.colour="magenta"

    randFloat = random.uniform(0.1, 0.2)
    for x in range(0, 150):
        Pbar.update()
        time.sleep(randFloat)

    Pbar.colour="green"


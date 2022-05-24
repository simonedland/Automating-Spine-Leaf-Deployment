from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
import time

def TurnOfCDP(node):
    node.run(task=netmiko_send_config, config_commands=["no cdp run"])

def TurnOnCDP(node):
    node.run(task=netmiko_send_config, config_commands=["cdp run", "cdp timer 5"])
    time.sleep(15)

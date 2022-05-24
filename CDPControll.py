from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config


def TurnOfCDP(node):
    node.run(task=netmiko_send_config, config_commands=["no cdp run"])

def TurnOnCDP(node):
    node.run(task=netmiko_send_config, config_commands=["cdp run"])

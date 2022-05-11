from nornir_netmiko.tasks import netmiko_send_command
def SaveRunningToStart(node):
    """preps a save command"""
    commandlist=["write mem"]

    #should not need to loop, but i have this for future use if needed
    for x in commandlist:
        node.run(task=netmiko_send_command, command_string=x, enable=True)
    pass
from cgitb import enable
from nornir.core.task import Task, Result
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from nornir_napalm.plugins.tasks import napalm_get
import time
from pingTest import ping
from resett import resetter

#todo:
#1. make a enviroment reset function that compleatly resetts the enviroment back to basic functionality
#2. tftp ssh deployment using option 82 (optional)
#3. client side almoaste equal settup, only difrence is in host. yaml file

startTime=time.time() #this is the start time of the program
nr = InitNornir(config_file="config.yaml") #this is the nornir object
singleHost = nr.filter(name="spine1.cmh") #this is the nornir object with only one host

def main():
    #nr.run(task=ping)
    #nr.run(task=resetter)
    #test = nr.run(task=netmiko_send_command, command_string="show ip int br")
    #print_result(test)
    pass

main() #run the main function


print(f"\n\n\n\n\n\n\n\n\n\nthe script took {time.time()-startTime} seconds") #prints how long the script took to run
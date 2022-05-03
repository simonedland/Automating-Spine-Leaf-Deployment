from nornir.core.task import Task, Result
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
import time

#todo:
#1. basic connectivity test
#2. make a enviroment reset function

startTime=time.time() #this is the start time of the program

nr = InitNornir(config_file="config.yaml") #this is the nornir object

singleHost = nr.filter(name="host1.cmh") #this is the nornir object with only one host

def main():
    print("test")
    

main() #run the main function


print(f"\n\n\n\n\nthe script took {time.time()-startTime} seconds") #prints how long the script took to run
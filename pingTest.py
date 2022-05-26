from tqdm import tqdm
import time
import os
#? probably no need for progress bar
def ping(node): #this is the ping test
    startTime=time.time() #this is the start time of the program
    pbar=tqdm(total=1)
    pbar.set_description(f"ping {node.host.hostname}")
    response = os.popen(f"ping {node.host.hostname}").read() #pings the host from the ssh server
    if "Received = 4" in response: #if the ping test was successful
        pbar.colour="green"
        pbar.update()
        pbar.close()
    else: #if the ping test was not successful
        pbar.colour="red"
        pbar.update()
    pbar.leave = False

    return 0, time.time()-startTime #returns the time it took to ping the


from tqdm import tqdm
import os
import time
def ping(node):
    #ping test
    pbar=tqdm(total=1)
    pbar.set_description(f"ping {node.host.hostname}")
    response = os.popen(f"ping {node.host.hostname}").read()
    if "Received = 4" in response:
        pbar.colour="green"
        pbar.update()
        time.sleep(0.2)
        pbar.close()
    else:
        pbar.colour="red"
        pbar.update()
        time.sleep(0.2)
    pbar.close()
    time.sleep(0.2)

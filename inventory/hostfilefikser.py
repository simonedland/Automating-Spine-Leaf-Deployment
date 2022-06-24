import yaml

#this is a hostfile generator
#it works uto 254 hosts in total
#edge nodes are placed in the last switchpair

counter=1
nr_of_spines=3
nr_of_leafs=10

hostname3octets="10.100.0."

mydict={}
for x in range(nr_of_spines):
    mydict.update({
        f"spine{counter}.cmh"
            :{"hostname":f"{hostname3octets}{counter}",
            "groups":[
                f"spine"
                ]}
        })
    counter+=1

y=0
z=1
for x in range(nr_of_leafs):
    if y == 2:
        z+=1
        y=0

    if x >= nr_of_leafs-2:
        mydict.update({
        f"leaf{x+1}.cmh"
            :{"hostname":f"{hostname3octets}{counter}", 
            "groups":[
                f"leaf", 
                "edge"
                ], 
            "data":{
                "switchpair":z
                }}
        })
    else:
        mydict.update({
        f"leaf{x+1}.cmh"
            :{"hostname":f"{hostname3octets}{counter}", 
            "groups":[
                f"leaf"
                ], 
            "data":{
                "switchpair":z
                }}
        })

    counter+=1
    y+=1

print(mydict)
with open('result.yml', 'w') as yaml_file:
    yaml_file.write("---\n")
    yaml.dump(mydict, yaml_file, sort_keys=False)
import yaml


counter=1
nr_of_spines=10
nr_of_leafs=10


mydict={}
for x in range(nr_of_spines):
    mydict.update({
        f"spine{counter}.cmh"
        :{"hostname":f"10.100.0.{counter}", 
        "groups":[f"spine"]}
        })
    counter+=1


y=0
z=1
for x in range(nr_of_leafs):
    if y == 2:
        z+=1
        y=0

    mydict.update({
        f"leaf{x+1}.cmh"
        :{"hostname":f"10.100.0.{counter}", 
        "groups":[f"leaf"], 
        "data":{"switchpair":z}}
        })
    counter+=1

    y+=1


print(mydict)
with open('result.yml', 'w') as yaml_file:
    yaml_file.write("---\n")
    yaml.dump(mydict, yaml_file)
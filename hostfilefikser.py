import yaml

mydict={}
for x in range(1,10):
    mydict.update({
        f"spine{x}.cmh"
        :{"hostname":x, "groups":[f"spine"]}

        })

d = {'A':'a', 'B':{'C':'c', 'D':'d', 'E':'e'}}
print(d)
print(mydict)
with open('result.yml', 'w') as yaml_file:
    yaml_file.write("---\n")
    yaml.dump(mydict, yaml_file)
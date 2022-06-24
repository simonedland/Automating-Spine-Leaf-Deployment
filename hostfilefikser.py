import yaml

mydict={}
for x in range(100):
    print (x)
    mydict.update({
        f"spine{x}.cmh"
        :{x:x}
        })

d = {'A':'a', 'B':{'C':'c', 'D':'d', 'E':'e'}}
print(d)

with open('result.yml', 'w') as yaml_file:
    yaml_file.write("---\n")
    yaml.dump(mydict, yaml_file)
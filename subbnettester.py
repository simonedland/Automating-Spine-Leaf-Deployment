from Subbnetter import subbnetter

test = subbnetter(nettwork=f"192.255.255.0",nettworkReq=[
            {"numberOfSubbnets":20, "requiredHosts":122},
            #{"numberOfSubbnets":2, "requiredHosts":5}
            ])
#print(test)

from NEW_subbnetter import subbnetter

test = subbnetter(nettwork=f"192.169.10.141",nettworkReq=[
            {"numberOfSubbnets":4, "requiredHosts":126},
            {"numberOfSubbnets":30, "requiredHosts":254*128},
            {"numberOfSubbnets":60, "requiredHosts":254*254*4},
            {"numberOfSubbnets":3, "requiredHosts":254*254*254}
            ])
print(test)
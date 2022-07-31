from Subbnetter import subbnetter

test = subbnetter(nettwork=f"192.255.255.0",nettworkReq=[
            {"numberOfSubbnets":20, "requiredHosts":122},
            #{"numberOfSubbnets":2, "requiredHosts":5}
            ])
#print(test)

from NEW_subbnetter import subbnetter

test = subbnetter(nettwork=f"192.169.10.141",nettworkReq=[
            {"numberOfSubbnets":4, "requiredHosts":2},
            {"numberOfSubbnets":3, "requiredHosts":254},
            {"numberOfSubbnets":1, "requiredHosts":254*254*4},
            {"numberOfSubbnets":1, "requiredHosts":254*254*254*5}
            ])
print(test)
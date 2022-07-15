from Subbnetter import subbnetter

test = subbnetter(nettwork=f"192.168.1.0",nettworkReq=[
            {"numberOfSubbnets":2, "requiredHosts":2},
            {"numberOfSubbnets":2, "requiredHosts":5}
            ])
#print(test)

from NEW_subbnetter import subbnetter

test = subbnetter(nettwork=f"192.168.1.0",nettworkReq=[
            {"numberOfSubbnets":2, "requiredHosts":2},
            {"numberOfSubbnets":3, "requiredHosts":5}
            ])
print(test)
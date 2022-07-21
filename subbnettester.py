from Subbnetter import subbnetter

test = subbnetter(nettwork=f"192.168.1.0",nettworkReq=[
            {"numberOfSubbnets":2, "requiredHosts":2},
            {"numberOfSubbnets":2, "requiredHosts":5}
            ])
#print(test)

from NEW_subbnetter import subbnetter

test = subbnetter(nettwork=f"192.168.1.123",nettworkReq=[
            #{"numberOfSubbnets":1, "requiredHosts":254*254},
            #{"numberOfSubbnets":1, "requiredHosts":254},
            {"numberOfSubbnets":10, "requiredHosts":1100}
            #{"numberOfSubbnets":20, "requiredHosts":30}
            ])
print(test)
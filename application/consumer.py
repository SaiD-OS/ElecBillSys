
class Consumer():
    def __init__(self,cursor,cid="",fname="",lname="",address="",taluka="",district="",pinCode="",meterId="",conType="",sanctionedLoad=10,contact=""):
        self.cid = cid
        self.fname = fname
        self.lname = lname
        self.address = address
        self.taluka = taluka
        self.district = district
        self.pinCode = pinCode
        self.meterId = meterId
        self.conType = conType
        self.sanctionedLoad = sanctionedLoad
        self.contact = contact
        self.talukas = ["PONDA", "PANAJI"]
        self.cidTalukas = ["PON", "PAN"]
        self.districts = ["SOUTH GOA","NORTH GOA"]
        self.cursor = cursor
    
    def validateTaluka(self):
        if self.taluka in self.talukas:
            return True
        else:
            return False

    def validateCId(self):
        self.cursor.execute('SELECT * FROM consumer WHERE ConID = %s', (self.cid))
        acc = self.cursor.fetchone()
        print(acc)
        if len(self.cid) == 11 and self.cid[:3].upper() in self.cidTalukas and acc == None:
            return True
        else:
            return False

    def validateDistrict(self):
        if self.district in self.districts:
            return True 
        else:
            return False

    def validateMeterID(self):
        self.cursor.execute('SELECT * FROM consumer WHERE MeterID = %s', (self.meterId))
        acc = self.cursor.fetchone()
        print(acc)
        print(len(self.meterId) == 14)
        print(self.meterId[0] == "1")
        print(self.meterId[1:4].upper() in self.cidTalukas)
        print(acc == None)
        if len(self.meterId) == 14 and self.meterId[0] == "1" and self.meterId[1:4].upper() in self.cidTalukas and acc == None:
            return True
        else:
            return False
    def insertConsumer(self):

        try:
            self.cursor.execute("INSERT INTO Consumer VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(self.cid,self.fname,self.lname,self.address,self.taluka,self.district,self.pinCode,self.meterId,self.conType,int(self.sanctionedLoad),self.contact))
            return True
        except:
            print("Exception")
            return False
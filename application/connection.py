import re
import pymysql
from datetime import date

class Connection:

    # initialise the connection whenever created 
    def __init__(self, conn, request=""):
        self.conn = conn
        self.cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request != "":
            try:
                self.connID = self.generateConnID()
                self.connAddress = request.form['inputConnAddress']
                self.connTaluka = request.form['inputConnTaluka']
                self.connDistrict = request.form['inputConnDistrict']
                self.connPin = request.form['inputConnPin']
                self.meterNo = request.form['inputMeterNo']
                self.conType = request.form['inputConnType']
                self.conNo = request.form['inputConNo'][2:]
                self.installationID = self.generateInstallID()
                self.mrId = self.generateMRID()
                self.installationDate = request.form['inputInstallationDate']
                print(f"instDT{self.installationDate}")
                self.connStatus = request.form['inputConnStatus']
                self.created = ""
                self.updated = ""
            except:
                print("Could not instantiate connection")

        


    def generateInstallID(self):
        try:
            self.cursor.execute('SELECT MAX(Installation_ID) as Installation_ID FROM connection')
            record = self.cursor.fetchone()
            if record:
                installID = record['Installation_ID'] + 1
                print(installID)
            else:
                # if the table is empty
                installID = 1000000001
        except Exception as e:
            print(e)
            print("Unable to generate InstallID")

        return installID
    
    # created using auto-increment (max of co_id + 1)
    def generateConnID(self):
        try:
            self.cursor.execute('SELECT MAX(Co_ID) as Co_ID FROM connection')
            record = self.cursor.fetchone()
            if record:
                connectID = record['Co_ID'] + 1
                print(connectID)
            else:
                # if the table is empty
                connectID = 100000000001
        except:
            print("Unable to generate connectID")

        return connectID
    

    # when provided with id initialize the variables
    def getConnection(self, connId):
        try:
            self.cursor.execute("SELECT * FROM connection WHERE Co_ID = %s",(connId))
            record = self.cursor.fetchone()
            self.connID = connId
            self.connAddress = record['Co_Address']
            self.connTaluka = record['Co_Taluka']
            self.connDistrict = record['Co_District']
            self.connPin = record['Co_Pin']
            self.meterNo = record['Meter_No']
            self.conType = record['Co_Type_ID']
            self.conNo = record['Con_ID']
            self.installationID = record['Installation_ID']
            self.installationDate = record['Installation_Date']
            self.connStatus = record['Co_Status']
            self.created = record['Created']
            self.updated = record['Updated']
            msg = "Connection Found"
            return msg, True
        except:
            msg="Unable to get connection"
            return msg, False

    def insertConnection(self):
        today = str(date.today())
        self.created = today
        self.updated = today
        print(f"jadoo nasha {self.connID}")
        print(f"jadoo nasha1 {self.conNo}")
        print(self.connAddress)
        print(self.installationID)
        try:
            print("Executing Insert Query")
            self.cursor.execute("INSERT INTO connection VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(self.connID,self.connAddress,self.connTaluka,self.connDistrict, self.connPin, self.meterNo, int(self.conType), self.conNo, self.installationID, self.installationDate, self.connStatus, self.created, self.updated))
            self.cursor.execute("INSERT INTO meter_reading (Meter_Reading_id,Meter_No, Co_ID,Meter_Reading,Read_Date,Meter_Status,Created,Updated,prev_date,prev_reading) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(self.mrId,self.meterNo, self.connID, 0, self.installationDate, "active", self.created, self.updated, self.installationDate, 0))

            self.conn.commit()
            msg = "Connection Inserted Successfully"
            return msg, True
        except Exception as e:
            print(e)
            msg="Unable to insert into connection"
            return msg, False
    
    def deleteConnection(self, connId):
        try:
            print("Executing Delete Query")
            self.cursor.execute("DELETE FROM connection WHERE Co_ID = %s",(connId))
            #record = self.cursor.fetchone()
            self.conn.commit()
            msg = "Successfully Deleted the Connection"
            return msg, True
        except Exception as e:
            print(e)
            msg ="Unable to delete connection"
            return msg, False

    def updateConnection(self, connId, cid,request):
        today = str(date.today())
        try:
            self.cursor.execute("SELECT Installation_ID, Installation_Date, Created FROM connection WHERE Co_ID = %s",(connId))
            record = self.cursor.fetchone()
            print("Executing update Query")
            self.connAddress = request.form['inputConnAddress']
            self.connTaluka = request.form['inputConnTaluka']
            self.connDistrict = request.form['inputConnDistrict']
            self.connPin = request.form['inputConnPin']
            self.meterNo = request.form['inputMeterNo']
            self.conType = request.form['inputConnType']
            self.conNo = cid
            self.installationID = record['Installation_ID']
            self.installationDate = request.form['inputInstallationDate']
            self.connStatus = request.form['inputConnStatus']
            self.created = record['Created']
            
            self.cursor.execute("UPDATE connection SET Co_Address = %s, Co_Taluka = %s, Co_District = %s, Co_Pin = %s, Meter_No = %s, Co_Type_ID = %s, Con_ID = %s, Installation_ID = %s, Installation_Date = %s, Co_Status = %s, Created = %s, Updated = %s WHERE Co_ID = %s",(self.connAddress, self.connTaluka, self.connDistrict, self.connPin, self.meterNo, self.conType, int(self.conNo), self.installationID, self.installationDate, self.connStatus, self.created, today, connId))
            self.conn.commit()
            msg="Successfully Deleted the Connection"
            return msg, True
        except Exception as e:
            print(e)
            msg="Unable to update connection"
            return msg, False

    def getConnectionByMeterNo(self,meterNo):
        self.cursor.execute("SELECT CO_ID from connection where Meter_No = %s",(meterNo))
        self.connID = self.cursor.fetchone()["CO_ID"]
        self.getConnection(self.connID)
    
    def generateMRID(self):
        self.cursor.execute("SELECT max(Meter_Reading_id ) as mid from meter_reading")
        record = self.cursor.fetchone()
        print(record)
        if record["mid"] == None:
            return 60000000000001
        else:
            return int(record['mid']) + 1
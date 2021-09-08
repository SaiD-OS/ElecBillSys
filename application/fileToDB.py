import pandas as pd
from datetime import datetime
from datetime import date
import pymysql
from pymysql.cursors import Cursor
from .Billing import Bill
from application import Billing

class MeterReading():
    columns = ['MeterReadingId', 'MeterNo', 'Fname', 'Lname','Address','Taluka','District','Pin', 'Contact', 'prev_date', 'prev_reading', 'Meter_Reading', 'Read_Date']
    #update the lis
    Talukas = {"PO":"Ponda", "TI":"Tiswadi"}
    def __init__(self, conn, id):
        # self.filename = 
        self.path = "C:\\Users\\sdharwadkar\\electricityBillingSystem\\application\\static\\file"
        #take filename from {decide later}
        self.id = id
        d = str(date.today())
        d = d.split('-')
        filename = f"{d[0]}{d[1]}"
        self.fileName = f'{self.id[:2]}-{filename}.csv'
        self.conn = conn
        self.cursor = conn.cursor(pymysql.cursors.DictCursor)

    def readFile(self):
        df = pd.read_csv(f'{self.path}\\{self.fileName}')
        print(df.columns == MeterReading.columns)
        for _, row in df.iterrows():
            print(f'row: {_}')
            print(row['MeterReadingId'],row["MeterNo"],row["prev_date"],row["prev_reading"],row["Read_Date"],row["Meter_Reading"])
            self.cursor.execute("SELECT CO_ID from connection where Meter_No = %s",(row["MeterNo"]))
            connID = self.cursor.fetchone()['CO_ID']
            id = self.generateID()
            try:
                self.cursor.execute("INSERT INTO meter_reading VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(id,row["MeterNo"],connID,row["Meter_Reading"],self.getDate(row["Read_Date"]),"Active",str(date.today()),str(date.today()),self.getDate(row["prev_date"]),row["prev_reading"]))
                bill = Bill(self.conn,row["MeterNo"],row["prev_date"],row["prev_reading"],row["Read_Date"],row["Meter_Reading"])
                bill.getAmount()
            except Exception as e:
                print(e)
        self.conn.commit()
        return True

        

    def createMeterReadingFile(self): 
        #get meter guy login id
        taluka = self.Talukas[self.id[:2]]
        self.cursor.execute("SELECT * FROM connection where Co_Taluka = %s ",(taluka))
        connections = self.cursor.fetchall()
        ls = []
        self.cursor.execute('SELECT MAX(Meter_reading_id) as md FROM meter_reading')
        record = self.cursor.fetchone()
        id = int(record['md'])
        print(id)
        for row in connections:
            print(row)
            #generate a meter reading ID
            id = id + 1
             #create database connection with pymysql dictionary
            self.cursor.execute("select Meter_Reading,Read_Date,Meter_Status from meter_reading where Co_ID = %s and Read_Date = (SELECT max(Read_Date) from Meter_Reading WHERE Co_ID = %s);",(row['Co_ID'],row['Co_ID']))
            reading = self.cursor.fetchone()
            print(f'Reading: {reading["Meter_Reading"]}')

            self.cursor.execute("SELECT Con_First_Name,Con_Last_Name,Con_Contact FROM consumer where Con_ID = %s ",(row['Con_ID']))
            consumer = self.cursor.fetchone()
            temp = [id,row['Meter_No'], consumer['Con_First_Name'],consumer['Con_Last_Name'],row['Co_Address'],row['Co_Taluka'],row['Co_District'],row['Co_Pin'],consumer['Con_Contact'],str(reading['Read_Date']),reading['Meter_Reading'],"",""]
            print(temp)
            ls.append(temp)
        df = pd.DataFrame(data=ls,columns=self.columns)
        csvData = df.to_csv()
        path_file = f'{self.path}\\{self.fileName}'
        df.to_csv(path_file,index=False)
        return csvData, self.fileName
        
    def getDate(self,date):
        temp = date.split("/")
        dat = f"{temp[2]}-{temp[0]}-{temp[1]}"
        return datetime.strptime(dat,'%Y-%m-%d').date()

    def generateID(self):
        self.cursor.execute("SELECT max(Meter_Reading_id ) as mid from meter_reading")
        record = self.cursor.fetchone()
        print(record)
        if record["mid"] == None:
            return 60000000000001
        else:
            return int(record['mid']) + 1
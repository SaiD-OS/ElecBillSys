from pymysql.cursors import Cursor
from .consumer import Consumer
from .connection import Connection
from datetime import timedelta
from datetime import date
from datetime import datetime
import pymysql
# from .fileToDB import MeterReading
class Bill():

    def __init__(self,conn,meterNo,prevDate,prevReading,readDate,reading):

        self.conn = conn
        self.cursor = conn.cursor(pymysql.cursors.DictCursor)
        self.cursor.execute("SELECT Co_Type_ID from connection where Meter_No = %s",(meterNo))
        self.connType = self.cursor.fetchone()['Co_Type_ID']
        self.prevDate = self.getDate(prevDate)
        self.currDate = self.getDate(readDate)
        self.prevReading = prevReading
        self.currReading = reading
        self.dueDate = self.generateDueDate()
        print(f"prev: {self.prevDate}, curr:{self.currDate},due:{self.dueDate}")
        # self.amount = self.getAmount()

    
    def getAmount(self):

        consumption = self.currReading - self.prevReading
        self.cursor.execute("SELECT Units_To from slab_charges WHERE From_Date = (SELECT MAX(From_Date) from slab_charges) and S_Charge_Type = %s and Con_Type_ID = %s",("EC",self.connType)) 
        temp = self.cursor.fetchall()
        slabs=[]
        for t in temp:
            slabs.append(t['Units_To'])
        print(slabs)

        #find the days passed between prev and current date
        billingPeriod = (self.currDate - self.prevDate).days
        print(billingPeriod)
        print(str(self.prevDate))
        self.cursor.execute("SELECT DISTINCT From_Date FROM slab_charges WHERE (From_Date >%s and From_Date <%s) or From_Date =(SELECT MAX(From_Date) from slab_charges where From_Date <=%s) ORDER BY From_Date Desc ",(str(self.prevDate),str(self.currDate),str(self.prevDate)))
        Temp = self.cursor.fetchall()
        dates = []
        for t in Temp:
            print(t)
            dates.append(t['From_Date'])
        #if prev reading date >= last change of slabs 
            #simple calculations 
        #else 
            #go uptill prev date >= last change and calculate for every change
        #fill the required tables  or return amount 
        #do not forget to update the billing calender

    def getCurrDate(self):
        try:
            print("Trying to Get Current Reading date")
            self.cursor.execute('SELECT Max(Read_Date) as currDate, Meter_Reading FROM Meter_Reading where Co_ID = %s',(self.connection.connID))
            acc = self.cursor.fetchone()
            currDate = acc['currDate']
            currReading = acc['Meter_Reading']
            return currDate
        except:
            print("unable to create cno")
            return 0

    def getPrevDate(self):
        #check for prev data in billing table
        #if no data then get the installation date asa prev date and make prev reading 0
        try:
            print("Trying to Get prev Reading date")
            self.cursor.execute('SELECT Installation_ID as prevDate FROM Connection where Co_ID = %s',(self.connection.connID))
            acc = self.cursor.fetchone()
            prevDate = acc['prevDate']
            return prevDate, 0
        except:
            print("unable to create cno")
            return 0

    def generateDueDate(self):
        return self.currDate + timedelta(days = 15)

    
    def jadoo(self):
        pass

    def getDate(self,date):
        temp = date.split("/")
        dat = f"{temp[2]}-{temp[0]}-{temp[1]}"
        return datetime.strptime(dat,'%Y-%m-%d').date()
    
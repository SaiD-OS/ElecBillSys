import pymysql
#create a conection object storing the database connection details
conn = pymysql.connect(
    host = 'localhost',
    database = 'test',
    user = 'root',
    password = '',
    cursorclass = pymysql.cursors.DictCursor
)

cursor = conn.cursor()


# createUserinfo stores query to create a new User_Info table
createUserInfo = """ CREATE TABLE User_Info (
    User_ID bigint PRIMARY KEY,
    User_Type varchar(8) NOT NULL,
    User_Name varchar(15) NOT NULL,
    Password varchar(70) NOT NULL,
    Created DATE NOT NULL,
    Updated DATE NOT NULL
);
"""

#createConnectionTable stores query to create a new Connection Table
createConnectionTable = """ CREATE TABLE Connection (
    Co_ID bigint PRIMARY KEY,
    Co_Address varchar(40) NOT NULL,
    Co_Taluka varchar(20) NOT NULL,
    Co_District varchar(20) NOT NULL,
    Co_Pin integer(6) NOT NULL,
    Meter_No bigint NOT NULL,
    Co_Type_ID int(3) NOT NULL,
    Con_ID bigint NOT NULL,
    Installation_ID integer(18) NOT NULL,
    Installation_Date Date NOT NULL,
    Co_Status boolean NOT NULL,
    Created DATE NOT NULL,
    Updated DATE NOT NULL,
    CONSTRAINT FK_connectionconID 
    FOREIGN KEY (Con_ID)
    REFERENCES Consumer(Con_ID)
);
"""

#createConsumerTable stores the query to create a new consumer table
createConsumerTable = """ CREATE TABLE Consumer (
    Con_ID bigint PRIMARY KEY AUTO_INCREMENT,
    Con_No varchar(12) NOT NULL UNIQUE,
    Con_First_Name varchar(30) NOT NULL,
    Con_Last_Name varchar(30) NOT NULL,
    Con_Address varchar(30) NOT NULL,
    Con_Taluka varchar(15) NOT NULL,
    Con_District varchar(15) NOT NULL,
    Con_Pin_Code varchar(6) NOT NULL,
    ConContact varchar(10) NOT NULL UNIQUE,
    Created DATE NOT NULL,
    Updated DATE NOT NULL
);
"""

#createDistributorTable stores the query to create a new distributor table
createDistributorTable = """ CREATE TABLE Distributor (
    DisID varchar(12) PRIMARY KEY,
    DisName varchar(40) NOT NULL,
    DisAddress varchar(40) NOT NULL,
    DisTaluka varchar(15) NOT NULL,
    DisDistrict varchar(15) NOT NULL,
    DisPincode varchar(6) NOT NULL,
    SupplyPerMonth real NOT NULL,
    DisContact varchar(10) NOT NULL UNIQUE,
    SupplyRate real NOT NULL
);
"""

# #createConBillsDetails stores the query to create a new consumer bills details table
# createConBillsDetails = """ CREATE TABLE Con_Bills_Details (
#     Bill_ID varchar(12) PRIMARY KEY,
#     Amount float NOT NULL,
#     Due_Date DATE NOT NULL,
#     Start_Date DATE NOT NULL,
#     End_Date DATE NOT NULL,
#     Con_ID integer(18) NOT NULL,
#     CONSTRAINT FK_conbilldetailsconID 
#     FOREIGN KEY (Con_ID)
#     REFERENCES Consumer(Con_ID)
#     ON DELETE CASCADE
# );
# """

#createConsumerTable stores the query to create a new Bill correction details table
createBillCorrecDetails = """ CREATE TABLE Bill_Correc_Details (
    Bill_Corr_ID integer(10) PRIMARY KEY,
    Bill_ID varchar(12) NOT NULL,
    Status varchar(10) NOT NULL,
    Comment varchar(500),
    Field_To_Correct varchar(20) NOT NULL,
    Con_ID bigint NOT NULL,
    Amount float NOT NULL,
    CONSTRAINT FK_billcorrecdetconID 
    FOREIGN KEY (Con_ID)
    REFERENCES Consumer(Con_ID)
    ON DELETE CASCADE
);
"""
#createNotice stores the query to create a new notice table
# createNotice = """ CREATE TABLE Notice (
#     NoticeID varchar(12) PRIMARY KEY,
#     BillID varchar(12) NOT NULL,
#     Fine float,
#     Days integer
# );
# """

#

#CreateConType stores a query to create a new connection type table
createConType = """ CREATE TABLE Connection_Type (
    Co_Type_ID integer(3) PRIMARY KEY,
    Co_Type varchar(10) NOT NULL,
    San_Load varchar(18) NOT NULL,
    Created Date NOT NULL,
    Updated Date NOT NULL
);
"""


#createMeterReading stores the query to create a new MeterReading table
createMeterReading = """ CREATE TABLE Meter_Reading (
    Meter_Reading_ID integer(3) 
    Meter_No varchar(12),
    Co_ID bigint NOT NULL,
    Meter_Reading varchar(18) NOT NULL,
    Read_Date DATE NOT NULL,
    Meter_Status varchar(10) NOT NULL,
    Created Date NOT NULL,
    Updated Date NOT NULL,
    CONSTRAINT FK_meterreadcoid 
    FOREIGN KEY (Co_ID)
    REFERENCES Connection(Co_ID)
);
"""

#createNoSlabCharges stores the query to create a new No_Slab_charges table
createNoSlabCharges = """ CREATE TABLE No_Slab_Charges (
    NSC_ID bigint PRIMARY KEY,
    Con_Type_ID integer(3) NOT NULL,
    NS_Charge_Type varchar(10) NOT NULL,
    NS_Charges varchar(11) NOT NULL,
    From_Date Date NOT NULL,
    Created Date NOT NULL,
    Updated Date NOT NULL,
    CONSTRAINT FK_noslabchargecontypeid
    FOREIGN KEY (Con_Type_ID)
    REFERENCES Connection_Type(Co_Type_ID)
);
"""

#createSlabCharges stores the query to create a new Slab_Charges table
createSlabCharges = """ CREATE TABLE Slab_Charges (
    SC_ID bigint PRIMARY KEY,
    Co_Type_ID integer(3) NOT NULL,
    S_Charge_Type varchar(10) NOT NULL,
    Units_From integer(11) NOT NULL,
    Units_To integer(11) NOT NULL,
    S_Charges varchar(11) NOT NULL,
    From_Date DATE NOT NULL,
    Created Date NOT NULL,
    Updated Date NOT NULL,
    CONSTRAINT FK_slabchargecontypeid
    FOREIGN KEY (Co_Type_ID)
    REFERENCES Connection_Type(Co_Type_ID)
);
"""

#createBillsData stores the query to create a new Bills_Data table
createBillsMaster = """ CREATE TABLE Bills_Data (
    BM_ID int(18) PRIMARY KEY,
    Meter_No varchar(12),
    Co_ID bigint NOT NULL,
    Con_ID bigint NOT NULL,
    Bill_Cal_ID bigint NOT NULL,
    Current_Read_Date Date,
    Current_Reading varchar(18) NOT NULL,
    Prev_Read_Date Date,
    Prev_Reading varchar(18),
    Consumption varchar(12),
    Due_Date DATE NOT NULL,
    Total_Amount real NOT NULL
    Reading_Remark varchar(12),
    Created Date NOT NULL,
    Updated Date NOT NULL
);
"""

#createBillDetail stores the query to create a new Bill_Detail table
createBillDetail = """ CREATE TABLE Bill_Detail (
    BD_ID bigint PRIMARY KEY,
    Amount_Type varchar NOT NULL,
    Total_Amount varchar NOT NULL,
    Created Date NOT NULL,
    Updated Date NOT NULL
);
"""

#billingCalInfo stores query to create a new BillingCalendarInfo table
createBillingCalInfo = """ CREATE TABLE Billing_Calendar_Info (
    Bill_Cal_ID bigint PRIMARY KEY,
    Co_ID bigint NOT NULL UNIQUE,
    Start_From date NOT NULL,
    Billing_Type varchar(8) NOT NULL,
    Time_Unit_Passed int(2) NOT NULL,
    Time_Delta varchar(4) NOT NULL,
    Created Date NOT NULL,
    Updated Date NOT NULL
);
"""


#createDiscoms stores query to create a new Discoms table
createDiscoms = """ CREATE TABLE Discoms (
    Discom_ID varchar(12) PRIMARY KEY,
    Discom_Name varchar(20) NOT NULL,
    Discom_Add varchar(30) NOT NULL,
    Discom_Taluka varchar(15) NOT NULL,
    Discom_District varchar(15) NOT NULL,
    Discom_Pin varchar(6) NOT NULL,
    Discom_Contact varchar(10) NOT NULL
);
"""

#createPaymentInfo stores query to create a new payment information table
createPaymentInfo = """ CREATE TABLE Payment_Info (
    Transaction_ID varchar(12) PRIMARY KEY,
    Bill_ID varchar(12) NOT NULL,
    Mode_Of_Payment varchar(8) NOT NULL,
    Payment_Date DATE NOT NULL,
    Amount_Paid float NOT NULL
);
"""

createRole = """ CREATE TABLE Role (
    Role_ID int PRIMARY KEY,
    Module_ID int NOT NULL,
    Module_Name varchar NOT NULL,
    Created date NOT NULL,
    updated date NOT NULL
);
"""

createUserRole = """ CREATE TABLE User_Role (
    UR_ID int PRIMARY KEY,
    user_id bigint NOT NULL,
    Role_ID int NOT NULL,
    Created date NOT NULL,
    updated date NOT NULL
);
"""

# cursor.execute(createConsumerTable)
#cursor.execute(createConType)
# cursor.execute(createConnectionTable)
#cursor.execute(createMeterReading)

#cursor.execute(createSlabCharges)
#cursor.execute(createNoSlabCharges)
#cursor.execute(createBillsData)

#cursor.execute(createDistributorTable)

#cursor.execute(createConBillsDetails)
# cursor.execute(createBillCorrecDetails)
# cursor.execute(createBillingCalInfo)
# cursor.execute(createDiscoms)
# cursor.execute(createPaymentInfo)

#sample data inserted into the tables
#connection_type
# cursor.execute(""" INSERT INTO connection_type VALUES(1,'Domestic','5.5','2021-09-06','2021-09-06'),
# 								  (2,'Agricultural','7.2','2021-09-06','2021-09-06'),
#                                   (3,'Commercial','20.3','2021-09-06','2021-09-06');) """)

# #no_slab_charges
# cursor.execute("""INSERT INTO no_slab_charges VALUES(101,1,'Fixed','60','2021-09-01','2021-09-06','2021-09-06'),
# 								  (102,2,'Fixed','30','2021-09-01','2021-09-06','2021-09-06'),
#                                   (103,3,'Fixed','100','2021-09-01','2021-09-06','2021-09-06'),
#                                   (104,1,'Subsidy','20','2021-09-01','2021-09-06','2021-09-06'),
# 								  (105,2,'Subsidy','50','2021-09-01','2021-09-06','2021-09-06'),
#                                   (106,3,'Subsidy','0','2021-09-01','2021-09-06','2021-09-06');""")

#

##slab charges

# cursor.execute("""INSERT INTO slab_charges VALUES(201,1,'EC',0,100,'1.40','2021-09-01','2021-09-06','2021-09-06'),
#  							   (202,1,'EC',101,200,'2.10','2021-09-01','2021-09-06','2021-09-06'),
#                                (203,1,'EC',201,300,'2.65','2021-09-01','2021-09-06','2021-09-06'),
#                                (204,1,'EC',301,400,'3.45','2021-09-01','2021-09-06','2021-09-06'),
#  						       (205,1,'EC',400,200000,'4.00','2021-09-01','2021-09-06','2021-09-06'),
#                                (206,1,'FPPCA',0,100,'0.1632','2021-09-01','2021-09-06','2021-09-06'),
#  							   (207,1,'FPPCA',101,200,'0.2398','2021-09-01','2021-09-06','2021-09-06'),
#                                (208,1,'FPPCA',201,300,'0.3233','2021-09-01','2021-09-06','2021-09-06'),
#                                (209,1,'FPPCA',301,400,'0.1640','2021-09-01','2021-09-06','2021-09-06'),
#  						       (210,1,'FPPCA',400,200000,'0.2410','2021-09-01','2021-09-06','2021-09-06'),
#                                (211,3,'EC',0,100,'3.40','2021-09-01','2021-09-06','2021-09-06'),
#  							   (212,3,'EC',101,200,'4.10','2021-09-01','2021-09-06','2021-09-06'),
#                                (213,3,'EC',201,300,'4.60','2021-09-01','2021-09-06','2021-09-06'),
#                                (214,3,'EC',301,400,'4.60','2021-09-01','2021-09-06','2021-09-06'),
#  						       (215,3,'EC',400,200000,'5.00','2021-09-01','2021-09-06','2021-09-06'),
#                                (216,3,'FPPCA',0,100,'0.1632','2021-09-01','2021-09-06','2021-09-06'),
#  							   (217,3,'FPPCA',101,200,'0.2398','2021-09-01','2021-09-06','2021-09-06'),
#                                (218,3,'FPPCA',201,300,'0.3233','2021-09-01','2021-09-06','2021-09-06'),
#                                (219,3,'FPPCA',301,400,'0.1640','2021-09-01','2021-09-06','2021-09-06'),
#  						       (220,3,'FPPCA',400,200000,'0.2410','2021-09-01','2021-09-06','2021-09-06');""")

conn.close()

from application.transaction import Transaction
from numpy import number
from application.user import User
from application.ditributor import Distributor
from flask import Flask, request, session, redirect, url_for, render_template, Response, flash
from flask.helpers import flash
from flaskext.mysql import MySQL
import pymysql
from pymysql import NULL, cursors 
from werkzeug.utils import secure_filename
import os
from .consumer import Consumer
from .fileToDB import MeterReading, Reading
from .Billing import Bill
import re 
from .connection import Connection
from .transaction import Transaction

import hashlib
import os
from datetime import date
# import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = 'weareateamofidkhowmany'

mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'test'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

app.config["CSV_UPLOADS"] = "C:\\Users\\adamle\\Documents\\ElecBillSys\\application\\static\\file\\get"
# app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["CSV"]

def allowed_file(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() == "CSV":
        return True
    else:
        return False

@app.route("/")
def home():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        roleId = session['role']
        uName = session['uName']
        uId = session['id']
        if roleId == "1":
            return render_template("dash.html", roleId = roleId, uName=uName, uId=uId)
        elif roleId == "2":
            return render_template("consumerDash.html", roleId = roleId, uName=uName, uId=uId)
        elif roleId == "3":
            return redirect(url_for('meterReading'))
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))



@app.route("/login", methods=['GET', 'POST'])
def login():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    msg = ''
    if request.method == 'POST'and 'inputCredentials' in request.form and 'inputId' in request.form and 'inputPassword' in request.form:
        username = request.form['inputId']
        print(username)
        password = request.form['inputPassword']
        # hash_password = generate_password_hash(password)
        # print(hash_password)
        role = request.form['inputCredentials']
        print(role)
        try:
            cursor.execute('SELECT * FROM login_info WHERE user_name = %s', (username))
            account = cursor.fetchone()
            pwd = account['password']
            uType = account['user_type']
        
        # print(f"Account {account}")
        # print(pwd)
        # print(uType == role)
        # print(check_password_hash(pwd,password))
        
            if account and check_password_hash(pwd,password) and uType == role :
                session['loggedin'] = True
                session['id'] = account['user_name']
                session['role'] = role
                print(role)
                if role == "1":
                    session["uName"] = "ADMINISTRATOR"
                    session["task"] = "add"
                    session["taskC"] = "add"
                    session["taskD"] = "add"
                    return redirect(url_for('dashboard'))
                elif account and role == "2":
                    cursor.execute("SELECT CONCAT(Con_First_Name , ' ' , Con_Last_Name) as Name from consumer where Con_No = %s", (session['id']))
                    session["uName"] = cursor.fetchone()['Name']
                    return redirect(url_for('dashboardCon'))
                    # return redirect(url_for('billDetail'))
                elif role == "3":
                    session["uName"] = "METER READER"
                    return redirect(url_for('meterReading'))
            
            else:
                msg = 'Please Enter Valid User Type, Username and Password'  

        except Exception as e:
            msg = e

    return render_template('login.html', msg=msg)

@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
   # Redirect to login page
    return redirect(url_for('login'))

@app.route("/adminCust", methods=["POST", "GET"])
def adminCust():
    if 'loggedin' in session and session['role'] == "1":
        roleId = session['role']
        task = session["task"]
        cid = ""
        fname = ""
        lname = ""
        address = ""
        taluka = ""
        district = ""
        pinCode = ""
        meterId = ""
        conType = ""
        contact = ""
        sanctionedLoad = 0
        print("hi")
        js = {"fname":fname, "lname":lname, "cid":cid, "address":address, "taluka":taluka, "district":district, "pinCode":pinCode, "meterId":meterId, "conType":conType, "contact":contact, "sanctionedLoad":sanctionedLoad}
        print("i am here")
        msgCat = 1

        if request.method == "POST" and 'task' in request.form:
            session["task"] = request.form['task']
            task = session["task"]
            print(session["task"])
            # Begin Add
            if task == "add":
                conn = mysql.connect()
                consumer = Consumer(conn,request)
                msg = None
                try:
                    msg, val = consumer.insertConsumer()
                    if val:
                        conn.commit()
                        msgCat=1
                        msg = f"Consumer Succefully Added. Consumer Number for generated Consumer is {consumer.cno}"
                except Exception as e:
                    print(f"outside${e}")
                    msg = e
                    msgCat=0
                finally:
                    conn.close()
                print(msg)
                # Only sending Role because user is Admin and username is Administrator
                return render_template("customerDataInput.html",msgCat=msgCat, msg = msg, val = task, js = js, roleId = roleId, uName=session["uName"], uId=session["id"])
            # End Add

            # Begin Update
            elif task == "upd":
                print(request.form['state'])
                cid = request.form['inputConFilID']
                conn = mysql.connect()
                consumer = Consumer(conn, request)
                msg = None
                # Messages for testing
                print("in Update")
                print(cid)
                if request.form['state'] == "1":
                    try:
                        print("actually updating")
                        cid = request.form['realID']
                        print(cid)
                        print("Printing cid")
                        updateCon = consumer.updateConsumer(cid, request)
                        if updateCon:
                            msg = "Customer updated Sucessfully"
                            msgCat=1
                        else:
                            msg = "Unable to update consumer"
                            msgCat=0
                    except:
                        msg = "Unable to update consumer"
                        msgCat=0
                    finally:
                        conn.close()
                else:
                    try:
                        msg, findCon = consumer.getConsumer(cid)
                        if not findCon:
                            msg = "Unable to find the consumer"
                            msgCat=0
                        else:
                            msgCat=1
                    except Exception as e:
                        msg=e
                        msgCat=0

                js = {"cid":cid,"fname":consumer.fname, "lname":consumer.lname, "address":consumer.address, "taluka":consumer.taluka, "district":consumer.district, "pinCode":consumer.pinCode, "email":consumer.email, "contact":consumer.contact}
                print(js)
                print(msg)
                return render_template("customerDataInput.html", msgCat=msgCat, msg=msg, val = task, js = js, roleId = roleId, uName=session["uName"], uId=session["id"])
            # End Update

            # Begin Delete
            elif task == "del":
                js = {"fname":"", "lname":"", "cid":"", "address":"", "taluka":"", "district":"", "pinCode":"", "meterId":"", "conType":"", "contact":"", "sanctionedLoad":""}
                cid = request.form['inputConFilID']
                print(cid)
                conn = mysql.connect()
                consumer = Consumer(conn, request)
                try:
                    consumer.getConsumer(cid)
                except Exception as e:
                    print(e)
                msg = None
                print("in Delete")
                print(request.form['state'])
                if request.form['state'] == "1":
                    try:
                        try:
                            print("actually deleting")
                            print(request.form['realID'])
                            cid = request.form['realID']
                            
                            val = consumer.deleteConsumer(cid)
                            
                            if val:
                                msg = "Customer deleted Sucessfully"
                                msgCat=1
                            else:
                                msg = "Unable to delete cutomer"
                                msgCat=0
                        except Exception as e:
                            print(e)
                            msg = "Unable to delete consumer"
                            msgCat=0
                    finally:
                        conn.close()
                else:
                    msg, val2 = consumer.getConsumer(cid)
                    js = {"cid":cid,"fname":consumer.fname, "lname":consumer.lname, "address":consumer.address, "taluka":consumer.taluka, "district":consumer.district, "pinCode":consumer.pinCode, "email":consumer.email, "contact":consumer.contact}
                    if not val2:
                        msg = "Unable to find the consumer"
                        msgCat=0
                    else:
                        msgCat=1
                
                print(js)
                print(msg)
                return render_template("customerDataInput.html",msgCat=msgCat, msg=msg, val = task, js = js, roleId = roleId, uName=session["uName"], uId=session["id"]) 
            #Delete end
        # User is loggedin show them the home page
        return render_template("customerDataInput.html", val = task, js = js, roleId = roleId, uName=session["uName"], uId=session["id"])
    # User is not loggedin redirect to login page

    return redirect(url_for('login'))

@app.route("/uploadFile", methods=["GET", "POST"])
def uploadFile():
    if request.method == "POST":
        roleId = session['role']
        if request.files:
            file = request.files["csvfile"]

            if file.filename == "":
                print("No filename")
                return redirect(request.url)

            if allowed_file(file.filename):
                filename = secure_filename(file.filename)

                file.save(os.path.join(app.config["CSV_UPLOADS"], filename))
                conn = mysql.connect()
                meterReading = MeterReading(conn)
                val = meterReading.readFile()
                if val:
                    print("file saved")
                    return redirect(request.url)

            else:
                print("That file extension is not allowed")
                return redirect(request.url)

    # Only sending role because user is admin            
    return render_template("meterReading.html", roleId = roleId, uName=session["uName"], uId=session["id"])

#Functionality has to be added
@app.route("/fileComplaint", methods=["GET", "POST"])
def fileComplaint(): 
    #adding check if the connection belongs to the consumer filing the complaint
    flag=0
    cNo = session["id"]
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if 'bid' in request.args:
        bid=request.args['bid']
    else:
        bid=""
    if bid == "" and request.method=="POST":
        #take values from the submitted form
        billId = request.form['inputBillId']
        connectionId = request.form['inputConnID']

        try:
            cursor.execute("SELECT Con_ID FROM connection WHERE Co_ID=%s",connectionId)
            record = cursor.fetchone()
            if(str(record["Con_ID"])!=str(cNo[2:])):
               flag=1
        except Exception as e:
            print(e)

        complaintCategorycoming = request.form['inputCompType']
        complaintCategory = 0
        if(complaintCategorycoming=="Technical"):
            complaintCategory = 1
        elif(complaintCategorycoming=="Bill Complaint"):
            complaintCategory = 2
        comment = request.form['inputCompDesc']
        created = str(date.today())
        updated = str(date.today())
        status = 0
        if(flag==0):
            try:
                #query to insert the new complaint into the bill_complain table
                cursor.execute("INSERT INTO bill_complain(`bill_id`,`co_id`,`category`,`status`,`comment`,`created`,`updated`) VALUES(%s,%s,%s,%s,%s,%s,%s)",(billId,connectionId,complaintCategory,status,comment,created,updated))
                print("Success!")
                conn.commit()
            except Exception as e:
                print(e)
        else:
            print("Consumer number dont match for connection!!")
    else:
        try:
            bill = Bill(conn)
            bill.getBill(bid)
            bill.cursor.execute("SELECT Co_ID FROM connection WHERE Meter_No =  %s",(bill.meterNo))
            coId = bill.cursor.fetchone()["Co_ID"]
            bill.amount = round(float(bill.amount),2)

            return render_template("fileComplaint.html", uName=session["uName"], uId=session["id"], bill=bill, coId=coId,compType=1)
        except Exception as e:
            print(e)

    return render_template("fileComplaint.html", uName=session["uName"], uId=session["id"], compType=0)

#route to handle the requests for complain list page
@app.route("/complainList", methods=["GET", "POST"])
def complainList():
    #get role and consumer number from session
    roleId = session['role']
    cNo = session["id"]
    #if user is an administrator
    if roleId == "1":
        conn = mysql.connect()
        complainCategory, complainIDs, connectionIDs, complainStatus, comments, created, updated, billId = [], [], [], [], [], [], [], []
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM bill_complain ORDER BY status ASC")
        #get all complaints descending status wise
        complains = cursor.fetchall()
        for complain in complains:
            complainCategory.append(complain["category"])
            complainIDs.append(complain["Bill_Comp_ID"])
            connectionIDs.append(complain["Co_ID"])
            complainStatus.append(complain["Status"])
            comments.append(complain["Comment"])
            created.append(complain["Created"])
            updated.append(complain["Updated"])
            if(complain["Bill_ID"]==NULL):
                billId.append(0)
            else:
                billId.append(complain["Bill_ID"])
        length = len(complainIDs)
        return render_template("complainList.html", uName=session["uName"], uId=session["id"],complainStatus=complainStatus,complainCategory=complainCategory,complainIDs=complainIDs,connectionIDs=connectionIDs,length=length, roleId = roleId, comments=comments,billId=billId)
    #if user is a consumer
    elif roleId == "2":
        conn = mysql.connect()
        complainCategory, complainIDs, connectionIDs, complainStatus, comments, created, updated = [], [], [], [], [], [], []
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM bill_complain WHERE Co_ID IN (SELECT Co_ID FROM connection WHERE Con_ID=%s)",cNo[2:])
        # get all complains made by the requesting consumer
        complains = cursor.fetchall()
        for complain in complains:
            complainCategory.append(complain["category"])
            complainIDs.append(complain["Bill_Comp_ID"])
            connectionIDs.append(complain["Co_ID"])
            complainStatus.append(complain["Status"])
            comments.append(complain["Comment"])
            created.append(complain["Created"])
            updated.append(complain["Updated"])
        length = len(complainIDs)
        return render_template("complainList.html", uName=session["uName"], uId=session["id"],complainStatus=complainStatus,complainCategory=complainCategory,complainIDs=complainIDs,connectionIDs=connectionIDs,length=length, roleId = roleId, comments=comments)


@app.route("/complainDetail")
def complainDetail():
    bid = request.args['id']
    print(f"BID : {bid}")
    conNo = session["id"]
    roleId = session['role']
    conn = mysql.connect()
    bill = Bill(conn)
    breakUP = bill.getBillBreakUp(bid)
    consumer = Consumer(conn)
    consumer.getConsumer(conNo)
    connection = Connection(conn,request)
    connection.getConnectionByMeterNo(bill.meterNo)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT San_Load, Con_Type FROM connection_type WHERE Con_Type_ID = %s ",(connection.conType))
        temp = cursor.fetchone()
        sancLoad = temp["San_Load"]
        conType = temp["Con_Type"]
        js = {"fname":consumer.fname, "amount":round(bill.amount,2),"instDt":connection.installationDate,"email":consumer.email, "instNo":connection.installationID,"lname":consumer.lname, "cid":consumer.cno, "address":connection.connAddress, "taluka":connection.connTaluka, "district":connection.connDistrict, "pinCode":connection.connPin, "meterId":connection.meterNo, "conType":conType, "contact":consumer.contact, "sanctionedLoad":sancLoad, "breakUP":breakUP}
        consumerName = consumer.fname + " " + consumer.lname
        print(js)
        return render_template("complainDetail.html", js=js, consumer=consumer, connection=connection, bill=bill, roleId = roleId, consumerNo = conNo, consumerName = consumerName)
    except Exception as e:
        print(e)

@app.route("/billTimeline")
def billTimeline():
    return render_template("billTimeline.html")  


@app.route("/billsList")
def billsList():
    cNo = session["id"]
    roleId = session['role']
    if roleId == "1":
        conn = mysql.connect()
        bill = Bill(conn)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        billNos,billDates, meterNos, amountDues, unitsConsumed, connectionIDs, prevDates, BillPaymentStatus = [],[],[],[],[],[],[],[]
        cursor.execute("SELECT Con_No FROM consumer")
        cNos = cursor.fetchall()
        print(cNos)
        for cNo in cNos:
            print(f"cNo = {cNo}[Con_No]")
            billNo,billDate, meterNo, amountDue, unitsConsume, connectionID, prevDate, BillPaymentStat = bill.getBillsByCNo(cNo["Con_No"])
            billNos.append(billNo)
            billDates.append(billDate)
            meterNos.append(meterNo)
            amountDues.append(amountDue)
            unitsConsumed.append(unitsConsume)
            connectionIDs.append(connectionID)
            prevDates.append(prevDate)
            BillPaymentStatus.append(BillPaymentStat)
        billNos = [j for sub in billNos for j in sub]
        billDates = [j for sub in billDates for j in sub]
        meterNos = [j for sub in meterNos for j in sub]
        amountDues = [j for sub in amountDues for j in sub]
        unitsConsumed = [j for sub in unitsConsumed for j in sub]
        connectionIDs = [j for sub in connectionIDs for j in sub]
        prevDates = [j for sub in prevDates for j in sub]
        BillPaymentStatus = [j for sub in BillPaymentStatus for j in sub]
        length = len(billNos)
        consumerName = ""
    elif roleId == "2":
        print(f"CNO = {cNo}")
        conn = mysql.connect()
        bill = Bill(conn)
        billNos,billDates, meterNos, amountDues, unitsConsumed, connectionIDs, prevDates,BillPaymentStatus = bill.getBillsByCNo(cNo)
        length = len(billNos)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM consumer WHERE Con_No = %s",(cNo))
        record = cursor.fetchone()
        consumerName = record['Con_First_Name'] + " " + record['Con_Last_Name']
    return render_template("billslist.html", uName=session["uName"], uId=session["id"],prevDates=prevDates,billNos=billNos,billDates=billDates,length=length,BillPaymentStatus=BillPaymentStatus,meterNos=meterNos,amountDues=amountDues,unitsConsumed=unitsConsumed,connectionIDs=connectionIDs, roleId = roleId, consumerNo = cNo, consumerName = consumerName)


@app.route("/billDetail")
def billDetail():
    bid = request.args['id']
    print(f"BID : {bid}")
    conNo = session["id"]
    roleId = session['role']
    conn = mysql.connect()
    bill = Bill(conn)
    breakUP = bill.getBillBreakUp(bid)
    consumer = Consumer(conn)
    consumer.getConsumer(bill.conNo)
    connection = Connection(conn,request)
    connection.getConnectionByMeterNo(bill.meterNo)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT San_Load, Con_Type FROM connection_type WHERE Con_Type_ID = %s ",(connection.conType))
    temp = cursor.fetchone()
    sancLoad = temp["San_Load"]
    conType = temp["Con_Type"]
    js = {"fname":consumer.fname, "amount":round(bill.amount,2),"instDt":connection.installationDate,"email":consumer.email, "instNo":connection.installationID,"lname":consumer.lname, "cid":consumer.cno, "address":connection.connAddress, "taluka":connection.connTaluka, "district":connection.connDistrict, "pinCode":connection.connPin, "meterId":connection.meterNo, "conType":conType, "contact":consumer.contact, "sanctionedLoad":sancLoad, "breakUP":breakUP}
    print(js)
    if roleId == "2":
        consumerName = consumer.fname + " " + consumer.lname
    else:
        consumerName = ""
    return render_template("billDetail.html", uName=session["uName"], uId=session["id"], js=js, connection = connection, consumer=consumer, bill = bill, consumerName = consumerName, consumerNumber = conNo, roleId = roleId) 

@app.route("/adminConn", methods=["POST", "GET"])
def adminConn():
    
    js = {"cid": "", "cno":"", "connType":"", "meterNo":"","caddress":"", "cdistrict":"", "ctaluka":"", "connStatus":"", "cpinCode":"", "installationDate":""}

    if 'loggedin' in session and session['role'] == "1":
        taskC = session["taskC"]
        roleId = session['role']
        js = {"cid": "", "cno":"", "connType":"", "meterNo":"","caddress":"", "cdistrict":"", "ctaluka":"", "connStatus":"", "cpinCode":"", "installationDate":""}
        msgCat=1

        if request.method == "POST" and 'taskC' in request.form:
                session["taskC"] = request.form['taskC']
                taskC = session["taskC"]
                print(session["taskC"])
                # Begin Add
                if taskC == "add":
                    conn = mysql.connect()

                    connection = Connection(conn, request)
                    msg = None
                    try:
                        msg, val = connection.insertConnection()
                        if val:
                            conn.commit()
                            msg = f"Connection Succefully Added. Connection ID for the Connection generated is {connection.connID}"
                            msgCat=1
                        else:
                            msg = "Unable to Add Connection"
                            msgCat=0
                    except:
                        msg = "Unable to Add Connection"
                        msgCat=0
                    finally:
                        conn.close()
                    print(msg)

                    # only roleId cuz user is admin
                    return render_template("connectionDataInput.html",msgCat=msgCat, msg = msg, val = taskC, js = js, roleId = roleId, uName=session["uName"], uId=session["id"])
                # End Add

                # Begin Delete
                elif taskC == "del":
                    
                    conid = request.form['inputConnFilID']
                    print(conid)
                    conn = mysql.connect()
                    connection = Connection(conn, request)
                    connection.getConnection(conid)
                    msg = None
                    print("in Delete")
                    print(request.form['stateC'])
                    if request.form['stateC'] == "1":
                        try:
                            try:
                                print("actually deleting")
                                print(request.form['realID'])
                                conid = request.form['realID']
                                
                                msg, val = connection.deleteConnection(conid)
                                
                                if val:
                                    msg = "connection deleted Sucessfully"
                                    msgCat=1
                                else:
                                    msg = "Unable to delete connection"
                                    msgCat=0
                            except:
                                msg = "Unable to delete connection"
                                msgCat=0
                        finally:
                            conn.close()
                    else:
                        msg, val2 = connection.getConnection(conid)
                        consumer1 = Consumer(conn)
                        consumer1.getConsumerbyId(connection.conNo)
                        js = {"cid": connection.connID, "cno":consumer1.cno, "connType":connection.conType, "meterNo":connection.meterNo,"caddress":connection.connAddress, "cdistrict":connection.connDistrict, "ctaluka":connection.connTaluka, "connStatus":connection.connStatus, "cpinCode":connection.connPin, "installationDate":connection.installationDate}
                        if not val2:
                            msg = "Unable to find the connection" 
                            msgCat=0
                        else:
                            msgCat=1
                    print(js)
                    return render_template("connectionDataInput.html",msgCat=msgCat,msg=msg, val = taskC, js = js, roleId = roleId, uName=session["uName"], uId=session["id"]) 
                # End Delete

                # Begin Update
                elif taskC == "upd":
                    connid = request.form['inputConnFilID']

                    conn = mysql.connect()
                    connection = Connection(conn, request)
                    msg = None

                    # Messages for testing
                    print("in Update")
                    print("ConnectionID : ",connid)

                    print(request.form['stateC'])
                    if request.form['stateC'] == "1":
                        try:
                            try:
                                print("actually updating")
                                connid = request.form['realID']
                                print("ConnectionID : ",connid)
                                consumer2 = Consumer(conn)
                                consumer2.getConsumerbyId(connection.conNo)
                                msg, updateConn = connection.updateConnection(connid, consumer2.cidpk,request)
                                if updateConn:
                                    msg = "Connection updated Sucessfully"
                                    msgCat=1
                                else:
                                    msg = "Unable to update connection"
                                    msgCat=0
                            except:
                                msg = "Unable to update connection"
                                msgCat=0
                        finally:
                            conn.close()
                    else:
                        msg, findConn = connection.getConnection(connid)
                        consumer1 = Consumer(conn)
                        consumer1.getConsumerbyId(connection.conNo)
                        print(connection.conNo)
                        js = {"cid": connection.connID, "cno":consumer1.cno, "connType":str(connection.conType), "meterNo":connection.meterNo,"caddress":connection.connAddress, "cdistrict":connection.connDistrict, "ctaluka":connection.connTaluka, "connStatus":connection.connStatus, "cpinCode":connection.connPin, "installationDate":connection.installationDate}
                        
                        if not findConn:
                            msg = "Unable to find the connection"
                            msgCat=0
                        else:
                            msgCat=1
                    
                    print(js)
                    print(msg)
                    return render_template("connectionDataInput.html",msg=msg, msgCat=msgCat, val = taskC, js = js, roleId = roleId, uName=session["uName"], uId=session["id"])
                # End Update
    return render_template("connectionDataInput.html", js=js, val=taskC, roleId = roleId)

    #return render_template("connectionDataInput.html", js=js, val=taskC, roleId = roleId, uName=session["uName"], uId=session["id"])

@app.route("/meterReading", methods=["GET", "POST"])
def meterReading():
    conn = mysql.connect()
    meterRead = MeterReading(conn,session['id'])
    roleId = session['role']
    # csv,filename = meterRead.createMeterReadingFile()
    if request.method=="POST":
        if 'formStateGet' in request.form:
            csv,filename = meterRead.createMeterReadingFile()
            return Response(csv,
                            mimetype="text/csv",
                            headers={"Content-disposition":
                                    f"attachment; filename={filename}"})
        elif 'formStatePost' in request.form:
            if request.files:
                file = request.files["uploadCsv"]
                if file.filename == "":
                    print("No filename")
                    return redirect(request.url)
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config["CSV_UPLOADS"], filename))
                    conn = mysql.connect()
                    meterReading = MeterReading(conn,session['id'])
                    val = meterReading.readFile()
                    if val:
                        print("file saved")
                        return redirect(request.url)
                else:
                    print("That file extension is not allowed")
                    return redirect(request.url)
    return render_template("meterReading.html", roleId = roleId, uName=session["uName"], uId=session["id"])

@app.route("/test")
def test():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    consumer = Consumer(conn,cursor)
    sql = consumer.validateCId()
    print(sql)
    return "<h1>testing<h1>"

@app.route("/dashboard")
def dashboard():
    if 'pageNo' in request.args:
        pageNo = int(request.args['pageNo'])- 1
    else:
        pageNo = 0
    if 'coNo' in request.args:
        cid = request.args['coNo']  
    else:
        cid = ""
    roleId = session['role']
    # userName = session['']
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if cid == "":
        cursor.execute("SELECT COUNT(*) as c FROM consumer")
        n = cursor.fetchone()["c"]
        import math
        n = math.ceil(n/5)
        cursor.execute("SELECT Con_No FROM consumer ORDER BY Con_No LIMIT %s, %s",(pageNo*5,5))
        conNumbers = cursor.fetchall()
        consumers = []
        numberOfConnections = []
        for conNumber in conNumbers:
            consumer = Consumer(conn)
            consumer.getConsumer(conNumber["Con_No"])
            consumers.append(consumer)
            cursor.execute("SELECT count(*) as c FROM connection WHERE Con_ID = %s",(consumer.cidpk))
            num = cursor.fetchone()["c"]
            numberOfConnections.append(num)
        print(consumers)
        print(numberOfConnections)
        print(n)
        return render_template("dash.html", roleId = roleId, consumers = consumers, pageNo=pageNo+1, num = numberOfConnections,n=n, uName=session["uName"], uId=session["id"])
    else:
        print()
        consumers = []
        numberOfConnections = []
        consumer = Consumer(conn)
        consumer.getConsumer(cid)
        consumers.append(consumer)
        cursor.execute("SELECT count(*) as c FROM connection WHERE Con_ID = %s",(consumer.cidpk))
        num = cursor.fetchone()["c"]
        numberOfConnections.append(num)
        return render_template("dash.html", roleId = roleId, num=numberOfConnections, pageNo=0, n=0, consumers = consumers, uName=session["uName"], uId=session["id"])

@app.route("/dashboardCon")
def dashboardCon():
    cNo = session["id"]
    roleId = session['role']
    conn = mysql.connect()
    connections = []
    if roleId == "2":
        if 'connId' in request.args:
            connId = request.args['connId']
            connection = Connection(conn)
            connection.getConnection(connId)
            connections.append(connection)
        else:
            connection = ""
        if connection == "":
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM consumer WHERE Con_No = %s",(cNo))
            record = cursor.fetchone()
            consumerName = record['Con_First_Name'] + " " + record['Con_Last_Name']
            print("Consumer Name")
            print(consumerName)
            cursor.execute("SELECT Co_ID FROM connection WHERE Con_ID = %s",(record['Con_ID']))
            records = cursor.fetchall()
            print(records)
            for record in records:
                connection = Connection(conn)
                connection.getConnection(record["Co_ID"])
                connections.append(connection)
            print(connections)
            return render_template("consumerDash.html",roleId=roleId,consumerName=consumerName,connections = connections, uName=session["uName"], uId=session["id"])
        else :
            return render_template("consumerDash.html",roleId=roleId,connections = connections, uName=session["uName"], uId=session["id"])
    return render_template("consumerDash.html",roleId=roleId,consumerName="", uName=session["uName"], uId=session["id"])

            # csv="Consumer No, Consumer First Name, Consumer Last Name, Connection No, Meter No, Address, District, Taluka, Pin Code, Contact, Email"


@app.route("/adminDistributor", methods=["POST", "GET"])
def adminDistributor():
    if 'loggedin' in session and session['role'] == "1":
        taskD = session["taskD"]
        roleId = session['role']
        js = {"disId":"","disCompName":"", "disAddress":"", "disDistrict":"", "disPincode":"", "suppplyMonth":"", "disContact":"", "supplyRate":"","created":"", "updated":""}

        if request.method == "POST" and 'taskD' in request.form:
            session["taskD"] = request.form['taskD']
            taskD = session["taskD"]
            print(session["taskD"])
            # Begin Add
            if taskD == "add":
                conn = mysql.connect()
                distributor = Distributor(conn, request)
                msg = None
                try:
                    val = distributor.insertDistributor()
                    if val:
                        conn.commit()
                        msg = "Distributor Successfully Added"
                    else:
                        msg = "Unable to Add Distributor"
                finally:
                    conn.close()
                print(msg)
                return render_template("distributorDataInput.html", msg = msg, val = taskD, js = js, roleId = roleId, uName=session["uName"], uId=session["id"])
            # End Add

            # Begin Update
            elif taskD == "upd":
                conn = mysql.connect()
                disId = request.form['inputDistFilID']

                distributor = Distributor(conn, request)
                msg = None
                # Messages for testing
                print("in Update")
                print(disId)
                print(request.form['stateD'])
                if request.form['stateD'] == "1":
                    try:
                        try:
                            print("actually updating")
                            disId = request.form['inputDistID']
                            print("Printing dis ID ", disId)
                            updateDis = distributor.updateDistributor(request, disId)
                            if updateDis:
                                msg = "Distributor updated Sucessfully"
                            else:
                                msg = "Unable to update distributor 1"
                        except:
                            msg = "Unable to update ditributor"
                    finally:
                        conn.close()
                else:
                    findDis = distributor.getDistributor(disId)
                    if not findDis:
                        msg = "Unable to find the Distributor"

                js = {"disId": disId ,"disCompName": distributor.disCompName, "disAddress": distributor.disAddress, "disDistrict": distributor.disDistrict, "disPincode": distributor.disPincode, "suppplyMonth": distributor.supplyPMonth, "disContact":distributor.disContact, "supplyRate": distributor.supplyRate,"created":distributor.created, "updated":distributor.updated}
                print(js)
                print(msg)
                return render_template("distributorDataInput.html", val = taskD, js = js, roleId = roleId, uName=session["uName"], uId=session["id"])
            # End Update

            # Begin Delete
            elif taskD == "del":
                js = {"disId":"","disCompName":"", "disAddress":"", "disDistrict":"", "disPincode":"", "suppplyMonth":"", "disContact":"", "supplyRate":"","created":"", "updated":""}
                disId = request.form['inputDistFilID'] #this statement is not working
                print("dis id from form ",disId)
                conn = mysql.connect()
                distributor = Distributor(conn, request)
                distributor.getDistributor(disId)
                
                msg = None
                print("in Delete")
                print("state ",request.form['stateD'])
                if request.form['stateD'] == "1":
                    try:
                        try:
                            print("actually deleting")
                            disId = request.form['inputDistFilID']
                            print("in delete dis id",disId)
                            
                            val = distributor.deleteDistributor(disId)
                            
                            if val:
                                msg = "Distributor deleted Sucessfully"
                            else:
                                msg = "Unable to delete Distributor"
                        except:
                            msg = "Unable to delete Distributor 1"
                    finally:
                        conn.close()
                else:
                    val2 = distributor.getDistributor(disId)
                    js = {"disId": disId ,"disCompName": distributor.disCompName, "disAddress": distributor.disAddress, "disDistrict": distributor.disDistrict, "disPincode": distributor.disPincode, "suppplyMonth": distributor.supplyPMonth, "disContact":distributor.disContact, "supplyRate": distributor.supplyRate,"created":distributor.created, "updated":distributor.updated}
                    if not val2:
                        msg = "Unable to find the Distributor"
                
                print(js)
                print(msg)
                return render_template("distributorDataInput.html", val = taskD, js = js, roleId = roleId, uName=session["uName"], uId=session["id"]) 
            #Delete end
        # User is loggedin show them the home page
        return render_template("distributorDataInput.html", val = taskD, js = js, roleId = roleId, uName=session["uName"], uId=session["id"])
    # User is not loggedin redirect to login page

    return redirect(url_for('login'))

@app.route("/paymentHistory")
def paymentHistory():
    cid = session["id"]
    transactions = []
    bids = []
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    consumer = Consumer(conn)
    consumer.getConsumer(cid)
    meterNos = consumer.getMeterNos()
    print(meterNos)
    for meterNo in meterNos:
        cursor.execute("SELECT BD_ID FROM bill_master WHERE Meter_No = %s",(meterNo))
        records = cursor.fetchall()
        if records:
            for record in records:
                t = Transaction(conn)
                try:
                    t.getTransactionByBid(record["BD_ID"])
                    print(t.status,t.trId,t.bid)
                    transactions.append(t)
                except Exception as e:
                    print(e)
    # print(transactions)
    print(len(transactions))
    for t in transactions:
        print(t.status)
        
    return render_template("paymentHistory.html", uName=session["uName"], uId=session["id"],transactions = transactions)

@app.route("/transaction",methods=['GET', 'POST'])
def transactionPage():
    conn = mysql.connect()
    stateT = 0
    if request.method == 'POST'and 'bid' in request.form and 'amount' in request.form:
        stateT = 1
        bid=request.form['bid']
        bill = Bill(conn)
        bill.getBill(bid)
        bill.amount = round(float(bill.amount),2)
        transaction = Transaction(conn, request)
        transaction.insertTransaction()
        return render_template("paymentPage.html", uName=session["uName"], uId=session["id"],transaction = transaction,bill = bill, stateT = stateT,crDate = str(date.today()))
    if "bid" in request.args:
        bid = request.args["bid"]
        bill = Bill(conn)
        bill.getBill(bid)
        bill.amount = round(float(bill.amount),2)
        return render_template("paymentPage.html", uName=session["uName"], uId=session["id"], bill = bill, stateT = stateT,crDate = str(date.today()))


@app.route("/billGenerate")
def billGenerate():
    conn = mysql.connect()
    reading = MeterReading(conn)
    MG1, MG2 = reading.sendData()
    js = {"MG1":MG1,"MG2":MG2}
    if "generate" in request.args:
        reading.readFile()
        return render_template("billGenerate.html",js = js,MG1=MG1, MG2=MG2, done ="1")
    return render_template("billGenerate.html",js = js,MG1=MG1, MG2=MG2)
    
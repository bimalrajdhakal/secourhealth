from flask import Flask, render_template, flash, redirect, request, url_for, session, logging
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,TextField,PasswordField
from functools import wraps
import random
import string
import datetime


app = Flask(__name__)  # instance of the flask

# config database

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'bimal'
app.config['MYSQL_DB'] = 'secourhealth_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init mysql
mysql = MySQL(app)

# home page
@app.route('/')
def home():
    return render_template('home.html')

# login page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get forms filed
        username = request.form['username']
        password_candidate = request.form['password']

        # create cursor
        cur = mysql.connection.cursor()
        # get user by username

        result = cur.execute("SELECT * FROM login_tbl WHERE user_name = %s", [username])

        if result > 0:
            # get stored password
            data = cur.fetchone()
            password = data['password']

            if password == password_candidate:
                #passed user password
                session['logged_in'] = True
                session['username'] = username
                session['profile_img'] = data['profile_img']
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid Username or Password !'
                return render_template('login.html', error=error)
            # close connection
            cur.close()

        else:
            error = 'User Name not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You are not authroized, please login', 'danger')
            return redirect(url_for('login'))
    return wrap
# logout

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


# forgot password
@app.route('/forgot_password/')
def forgot_password():
    return render_template('forgot_password.html')

# dashboard

@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')
# agent page

@app.route('/agent')
@is_logged_in
def agent():
    # display agent data from database to table
        # create cursor
    cur=mysql.connection.cursor() 
    # fetch agent_tbl from database
    
    result =cur.execute("SELECT * FROM agent_tbl")

    agentdata=cur.fetchall() 

    if result > 0:
        return render_template('agent.html',agentdata=agentdata)
    else:
        msg='No agent data found in database'
        return render_template('agent.html',msg=msg) 
    
     # close connection
    cur.close()

    return render_template('agent.html',agentdata=agentdata)

# agent class
class AgentForm(Form):
    fname=StringField()
    lname=StringField()
    email=StringField()
    mobno=StringField()
    addressline1=StringField()
    addressline2=StringField()
    addressline3=StringField()
    pincode=StringField()
    imeino=StringField()
    dob=StringField()


# add_agent 
@app.route('/add_agent',methods=['GET','POST'])
@is_logged_in
def add_agent():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        mobno = request.form['mobno']
        addressline1 = request.form['addressline1']
        addressline2 = request.form['addressline2']
        addressline3 = request.form['addressline3']
        pincode = request.form['pincode']
        imeino = request.form['imeino']
        dob = request.form['dob']
        utype = 'agent'
        password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

        # create cursor
        cur = mysql.connection.cursor()
        # execute query
        cur.execute("INSERT INTO agent_tbl(fname,lname,email,mobno,addressline1,addressline2,addressline3,pincode,imeino,dob)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (fname, lname, email, mobno, addressline1, addressline2, addressline3, pincode, imeino, dob))
        # insert agent cridential into login table
        cur.execute("INSERT INTO login_tbl(user_name,password,user_type)VALUES (%s,%s,%s)",
                    (email,password,utype))
        # commit to db
        mysql.connection.commit()

        #close the connection
        cur.close()
    return render_template('add_agent.html')

# edit agent
@app.route('/edit_agent/<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_agent(id):
    # create cursor 
    cur=mysql.connection.cursor()
    #get agent by id
    result=cur.execute("SELECT * FROM agent_tbl WHERE agent_id=%s",[id])

    agent=cur.fetchone()
    # get form
    form=AgentForm(request.form)
    # populate agent form fields
    form.fname.data=agent['fname']
    form.lname.data=agent['lname']
    form.email.data=agent['email']
    form.mobno.data=agent['mobno']
    form.addressline1.data=agent['addressline1']
    form.addressline2.data=agent['addressline2']
    form.addressline3.data=agent['addressline3']
    form.pincode.data=agent['pincode']
    form.imeino.data=agent['imeino']
    form.dob.data=agent['dob']

    if request.method == 'POST':
        fname=request.form['fname']
        lname=request.form['lname']
        email=request.form['email']
        mobno=request.form['mobno']
        addressline1=request.form['addressline1']
        addressline2=request.form['addressline2']
        addressline3=request.form['addressline3']
        pincode=request.form['pincode']
        imeino=request.form['imeino']
        dob=request.form['dob']

        # create cursor 

        cur = mysql.connection.cursor()
        # execute
        cur.execute("UPDATE agent_tbl SET fname=%s,lname=%s,email=%s,mobno=%s,addressline1=%s,addressline2=%s,addressline3=%s,pincode=%s,imeino=%s,dob=%s WHERE agent_id=%s",(fname,lname,email,mobno,addressline1,addressline2,addressline3,pincode,imeino,dob,id))
        # commit
        mysql.connection.commit()
        # close connection
        cur.close()
        flash('Agent info updated and saved successfully','success')
        return redirect(url_for('agent'))
    return render_template('edit_agent.html',form=form)

# view agent 
@app.route('/view_agent/<string:id>')
@is_logged_in
def view_agent(id):
    # create cursor 
    cur=mysql.connection.cursor()
    #get agent by id
    result=cur.execute("SELECT * FROM agent_tbl WHERE agent_id=%s",[id])

    agent=cur.fetchone()
    # get form
    form=AgentForm(request.form)
    # populate agent form fields
    form.fname.data=agent['fname']
    form.lname.data=agent['lname']
    form.email.data=agent['email']
    form.mobno.data=agent['mobno']
    form.addressline1.data=agent['addressline1']
    form.addressline2.data=agent['addressline2']
    form.addressline3.data=agent['addressline3']
    form.pincode.data=agent['pincode']
    form.imeino.data=agent['imeino']
    form.dob.data=agent['dob']

    return render_template('view_agent.html',form=form)

# delete agent 
@app.route('/delete_agent/<string:id>')
@is_logged_in
def delete_agent(id):
    # crete cursor
    cur=mysql.connection.cursor()

    #execute 
    cur.execute("DELETE FROM agent_tbl WHERE agent_id=%s",[id])
    # commit
    mysql.connection.commit()
    # close connection
    cur.close()
    return redirect(url_for('agent'))

# location registeration 

@app.route('/reg_location',methods=['GET','POST'])
@is_logged_in
def reg_location():
    if request.method == 'POST':
        hnobldg = request.form['hnobldg']
        street = request.form['street']
        landmark = request.form['landmark']
        area = request.form['area']
        pincode = request.form['pincode']
        lat = request.form['lat']
        lng = request.form['lng']
        runningadd = request.form['runningadd']
        loc_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        # create cursor
        cur = mysql.connection.cursor()
        # data insert into location registeration table
        cur.execute("INSERT INTO location_reg_tbl(loc_id,hno,street,landmark,area,pincode,lat,lng,runnadd)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (loc_id, hnobldg, street, landmark, area, pincode, lat,lng, runningadd))
        # commit to db
        mysql.connection.commit()

        #close the connection
        cur.close()
        return redirect(url_for('reg_location'))
    return render_template('reg_location.html')

# Manage Location page

@app.route('/location')
@is_logged_in
def location():
    # display location  data from database to table
    # create cursor
    cur=mysql.connection.cursor() 
    # fetch location_reg_tbl from database
    
    result =cur.execute("SELECT * FROM location_reg_tbl")

    locdata=cur.fetchall() 

    if result > 0:
        return render_template('location.html',locdata=locdata)
    else:
        msg='No agent data found in database'
        return render_template('location.html',msg=msg) 
    
     # close connection
    cur.close()

    return render_template('location.html',locdata=locdata)

# register location class class
class LocationForm(Form):
    loc_id=StringField()
    hno=StringField()
    street=StringField()
    landmark=StringField()
    area=StringField()
    pincode=StringField()
    lat=StringField()
    lng=StringField()
    runnadd=StringField()

# edit registered location
@app.route('/edit_location/<string:id>', methods=['GET','POST'])
@is_logged_in
def edit_location(id):
    # create cursor 
    cur=mysql.connection.cursor()
    #get location by id
    result=cur.execute("SELECT * FROM location_reg_tbl WHERE loc_id=%s",[id])

    location=cur.fetchone()
    # get form
    form=LocationForm(request.form)
    # populate location form fields
    form.hno.data=location['hno']
    form.street.data=location['street']
    form.landmark.data=location['landmark']
    form.area.data=location['area']
    form.pincode.data=location['pincode']
    form.lat.data=location['lat']
    form.lng.data=location['lng']
    form.runnadd.data=location['runnadd']

    if request.method == 'POST':
        hno=request.form['hno']
        street=request.form['street']
        landmark=request.form['landmark']
        area=request.form['area']
        pincode=request.form['pincode']
        lat=request.form['lat']
        lng=request.form['lng']
        runnadd=request.form['runnadd']

        # create cursor 

        cur = mysql.connection.cursor()
        # execute
        cur.execute("UPDATE location_reg_tbl SET hno=%s,street=%s,landmark=%s,area=%s,pincode=%s,lat=%s,lng=%s,runnadd=%s WHERE loc_id=%s",
        (hno,street,landmark,area,pincode,lat,lng,runnadd,id))
        # commit
        mysql.connection.commit()
        # close connection
        cur.close()
        flash('Location info updated and saved successfully','success')
        return redirect(url_for('location'))
    return render_template('edit_location.html',form=form)

# view agent 
@app.route('/view_location/<string:id>')
@is_logged_in
def view_location(id):
    # create cursor 
    cur=mysql.connection.cursor()
    #get location by id
    result=cur.execute("SELECT * FROM location_reg_tbl WHERE loc_id=%s",[id])

    location=cur.fetchone()
    # get form
    form=LocationForm(request.form)
    # populate registered form fields
    form.loc_id.data=location['loc_id']
    form.hno.data=location['hno']
    form.street.data=location['street']
    form.landmark.data=location['landmark']
    form.area.data=location['area']
    form.pincode.data=location['pincode']
    form.lat.data=location['lat']
    form.lng.data=location['lng']
    form.runnadd.data=location['runnadd']
    return render_template('view_location.html',form=form)

# delete registered location 
@app.route('/delete_location/<string:id>')
@is_logged_in
def delete_location(id):
    # crete cursor
    cur=mysql.connection.cursor()

    #execute 
    cur.execute("DELETE FROM location_reg_tbl WHERE loc_id=%s",[id])

    # commit
    mysql.connection.commit()
    # close connection
    cur.close()
    return redirect(url_for('location'))

#create questions 
@app.route('/create_question',methods=['GET','POST'])
@is_logged_in
def create_question():
    if request.method == 'POST':
        ques= request.form['question']
        questype=request.form['questype']
        ques_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        status='New'
        # crete cursor
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO question_master_tbl(ques_id,question,ques_type,status)VALUES (%s,%s,%s,%s)",
                    (ques_id, ques, questype,status))
        # commit
        mysql.connection.commit()
        # close connection
        cur.close()
        options = []
        if questype=='objective':
            for i in range(1,11,1):
                key = "option" + str(i)
                #print key
                if key in request.form:
                    print request.form[key]
                    options.append(request.form[key])
                    print options
            cur=mysql.connection.cursor()
            for option in options:
                print option
                cur.execute("INSERT INTO options_master_tbl(ques_id,option1)VALUES(%s,%s)",(ques_id,option))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('create_question'))
        return redirect(url_for('create_question'))
    return render_template('createques.html')

# Manage Question page

@app.route('/question')
@is_logged_in
def manage_ques():
    # display question  data from database to table
    # create cursor
    cur=mysql.connection.cursor() 
    # fetch question_master_tbl from database
    
    result =cur.execute("SELECT * FROM question_master_tbl where status='New'")

    qdata=cur.fetchall() 

    if result > 0:
        return render_template('manageques.html',qdata=qdata)
    else:
        msg='No Question data found in database'
        return render_template('manageques.html',msg=msg) 
    
     # close connection
    cur.close()

    return render_template('manageques.html',qdata=qdata)


# view question 
@app.route('/view_question/<string:id>')
@is_logged_in
def view_question(id):
    # create cursor 
    cur=mysql.connection.cursor()
    #get question by id
    result=cur.execute("SELECT * FROM question_master_tbl WHERE ques_id=%s",[id])
    quesdata=cur.fetchone()
    if quesdata['ques_type']=='objective':
         result=cur.execute("SELECT option1 FROM options_master_tbl WHERE ques_id=%s",[id])
         optiondata=cur.fetchall()
         return render_template('view_question.html',data=quesdata,opdata=optiondata)
    return render_template('view_question.html',data=quesdata)

# delete questions
@app.route('/delete_question/<string:id>')
@is_logged_in
def delete_question(id):
    # crete cursor
    cur=mysql.connection.cursor()

    #execute 
    cur.execute("DELETE FROM question_master_tbl WHERE ques_id=%s",[id])
    cur.execute("DELETE FROM options_master_tbl WHERE ques_id=%s",[id])
    # commit
    mysql.connection.commit()
    # close connection
    cur.close()
    return redirect(url_for('manage_ques'))

# create survey 
@app.route('/create_survey',methods=['GET','POST'])
@is_logged_in
def createSurvey():
    if request.method == 'POST':
        agentid=request.form['agentid']
        locid=request.form['locid']
        quesid=request.form.getlist('quesid')
        start_date=request.form['startdate']
        end_date=request.form['enddate']
        status='New'
        created_date = datetime.date.today()
        cur=mysql.connection.cursor()
        for quesdata in quesid:
            cur.execute("INSERT INTO survey_master_tbl(agentid,loc_id,ques_id,start_date,end_date,status,created_date)VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (agentid,locid,quesdata,start_date,end_date,status,created_date))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('createSurvey'))
    cur=mysql.connection.cursor()
    result = cur.execute("SELECT ques_id,question FROM question_master_tbl")
    quesdata=cur.fetchall()
    if result > 0:
        return render_template('createsurvey.html',quesdata=quesdata)
    else:
        msg='No Questions  data found in database'
        return render_template('createsurvey.html',msg=msg)
    # if request.method == 'POST':
    #     agentid=request.form['agentid']
    #     print agenid
    #     locid=request.form['locid']
    #     print locid
    #     #quesid=request.form.quesid.data
    #     start_date=request.form['startdate']
    #     print start_date
    #     end_date=request.form['enddate']
    #     print end_date
    #     status='New'
    #     created_date = datetime.date.today()
    #     cur.execute("INSERT INTO survey_master_tbl(agentid,loc_id,ques_id,start_date,end_date,status,created_date)VALUES(%s,%s,%s,%s,%s,%s,%s)",
    #             (agentid,locid,quesid,start_date,end_date,status,created_date))
    #     mysql.connection.commit()
    #     cur.close()
    #     return redirect(url_for('createSurvey'))
    return render_template('createsurvey.html',quesdata=quesdata)

# @app.route('/api/get_somedata/<string:asd>')
# def get_somedata(asd):
#     a = {"asd":"asd"}
#     json = demjson.encode(q)
#     return json


# checking app is running or not and defining secrete key for session
if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)

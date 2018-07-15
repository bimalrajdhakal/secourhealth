from flask import Flask, render_template, flash, redirect, request, url_for, session, logging
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,TextField,PasswordField
from functools import wraps
import random
import string
import datetime
import demjson

api = Flask(__name__)  # instance of the flask

# config database

api.config['MYSQL_HOST'] = 'localhost'
api.config['MYSQL_USER'] = 'root'
api.config['MYSQL_PASSWORD'] = 'bimal'
api.config['MYSQL_DB'] = 'secourhealth_db'
api.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init mysql
mysql = MySQL(api)

#login page

@api.route('/api/login/',methods=['GET','POST'])
def login():
    if request.method=='GET':
        username=request.args['username']
        password_candidate=request.args['password']
        # create cursor
        cur = mysql.connection.cursor()
        # get user by username
        result = cur.execute("SELECT * FROM login_tbl WHERE user_type='agent' and user_name = %s", [username])
        r = {}
        if result > 0:
            # get stored password
            data = cur.fetchone()
            password = data['password']
            user_type=data['user_type']
            if password == password_candidate:
                r['status'] = "Success"
                r['result'] = data
                #passed user password
                session['logged_in'] = True
                session['username'] = username
                session['user_type']=data['user_type']
                session['profile_img'] = data['profile_img']
                return demjson.encode(r)
            else:
                error = 'Invalid Username or Password !'
                r['status']='Failed'
                r['error']=error
                return demjson.encode(r)
                # close connection
        
        else:
            error = 'User Name not found'
            r['status']='NF'
            r['error']=error
            return demjson.encode(r)
        cur.close()
        return demjson.encode(r)

# register person 
@api.route('/api/register/',methods=['GET','POST'])
def register_Person():
    if request.method == 'GET':
        full_name = request.args['full_name']
        address = request.args['address']
        email_id = request.args['email_id']
        mobile_no = request.args['mobile_no']
        company =   request.args['company']
        registered_date=datetime.date.today()
        r = {}
        # create cursor
        cur = mysql.connection.cursor()
        # execute query
        cur.execute("INSERT INTO register_person_tbl(full_name,address,email_id,mobile_no,company,registered_date)VALUES (%s,%s,%s,%s,%s,%s)",
                    (full_name, address, email_id, mobile_no, company, registered_date))
        # commit to db
        mysql.connection.commit()
        
        #close the connection
        cur.close()
        r['status'] = "Success"
    return demjson.encode(r)
# agent page

@api.route('/api/viewarea/',methods=['GET','POST'])
def showAssignedArea():
    # display agent data from database to table
    # create cursor
    cur=mysql.connection.cursor() 
    # fetch agent_tbl from database
    #email=session['username']
    email='n@gmail.com'
    r = {}
    result =cur.execute("SELECT agent_id FROM agent_tbl where email=%s",[email])
    agentid=cur.fetchone()  
    # result =cur.execute("SELECT loc_id FROM survey_master_tbl where agentid=%s",[agentid['agent_id']])
    # loc_ids=cur.fetchall() 

    result =cur.execute("SELECT distinct area,loc_id FROM survey_master_tbl  inner join location_reg_tbl  USING(loc_id) WHERE agentid=%s",[agentid['agent_id']])
    data=cur.fetchall()
    r['status'] = "Success"
    r['result'] = data
     # close connection
    cur.close()

    return demjson.encode(r)

if __name__ == '__main__':
    api.secret_key = 'secret123'
    api.run('192.168.43.86',debug=True,port=5000)

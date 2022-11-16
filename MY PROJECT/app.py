
import re
from collections import UserDict

import ibm_db
import ibm_db_dbi as dbi
import os

import sys

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)

app = Flask(__name__)
app.secret_key = 'a'

conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=ba99a9e6-d59e-4883-8fc0-d6a8c9f7a08f.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=31321;SECURITY=SSL;SSLServerCertificate=Certificate.crt;UID=fqd68289;PWD=Pt7Lr9FUjtzoM73p",'','')

#homepage
@app.route("/home")
def home():
    return render_template("homepage.html")
@app.route("/")
def add():
    return render_template("home.html")


#signup or reg
@app.route("/signup")
def signup():
    return render_template("signup.html")
@app.route('/register', methods =['GET', 'POST'])
def register():
    global userid
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        sql="SELECT * FROM data WHERE username=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
                    msg = 'name must contain only characters and numbers !'
        else:
            insert_sql = "INSERT INTO Data VALUES (?, ?, ?)"
            stmt = ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(stmt, 1, username)
            ibm_db.bind_param(stmt, 2, email)
            ibm_db.bind_param(stmt, 3, password)
            ibm_db.execute(stmt)
            msg = 'You have successfully registered !'
    return render_template('signup.html', msg = msg)





#login
@app.route("/signin")
def signin():
    return render_template("login.html")
@app.route('/login',methods =['GET', 'POST'])
def login():
    global userid
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        stmt = ibm_db.prepare(conn,'SELECT * FROM Data WHERE username= ?AND password = ?')
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print (account)
        if account:
            session['loggedin'] = True
            session['id']=account['USERNAME']
            userid=account['USERNAME']=account['USERNAME']
            return redirect('/home')
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)


#add

@app.route("/add")
def adding():
    return render_template('add.html')
@app.route('/addexpense',methods=['GET', 'POST'])
def addexpense():
    if request.method == 'POST':
        date = request.form['date']
        expensename = request.form['expensename']
        amount = request.form['amount']
        paymode = request.form['paymode']
        category = request.form['category']
        insert_sql ="INSERT INTO expenses VALUES (?, ?, ?, ?, ?, ?)"
        stmt = ibm_db.prepare(conn,insert_sql)
        ibm_db.bind_param(stmt, 1, userid)
        ibm_db.bind_param(stmt, 2, date)
        ibm_db.bind_param(stmt, 3, expensename)
        ibm_db.bind_param(stmt, 4, amount)
        ibm_db.bind_param(stmt, 5, paymode)
        ibm_db.bind_param(stmt, 6, category)
        ibm_db.execute(stmt)
        session['loggedin']=True
        print(date + " " + expensename + " " + amount + " " + paymode + " " + category)
        print(session["id"])
    return redirect('/display')
       
 #display graph
@app.route("/display")
def display():
    print(session["id"])
    query = "SELECT * FROM expenses ORDER BY 'dates' DESC"
    stmt = ibm_db.exec_immediate(conn,query)
    row= ibm_db.fetch_tuple(stmt )
    while(row):
        print("%s,%s,%s,%s,%s,%s"%(str(row[0]),str(row[1]),str(row[2]),str(row[3]),str(row[4]),str(row[5])))
        row= ibm_db.fetch_tuple(stmt )
        print(str(row[1]))
        print(str[row[2]])
        print(str(row[4]))
        print(str(row[5]))
        
        
    return render_template('display.html',)
     




#del data
@app.route('/delete/<string:id>', methods = ['POST', 'GET' ])
def delete():
    stmt = ibm_db.prepare(conn,'DELETE FROM expenses WHERE userid=?')
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print('deleted successfully')
    return render_template('display.html' , account=account)



#update 
@app.route('/edit/<id>', methods = ['POST', 'GET' ])
def edit():
    sql='SELECT * FROM expenses WHERE userid =?'
    row= ibm_db.prepare(conn,sql)
    ibm_db.execute(row)
    print(row[0])
    return render_template('edit.html', expenses = row[0])



@app.route('/update/<id>', methods = ['POST'])
def update():
  if request.method == 'POST' :
    date = request.form['date']
    expensename = request.form['expensename']
    amount = request.form['amount']
    paymode = request.form['paymode']
    category = request.form['category']
    sql="UPDATE expenses SET date = ? , expensename = ? , amount = ?, paymode = ?, category = ? WHERE expenses.userid = ? ",(date, expensename, amount, str(paymode), str(category),userid)
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt, 1, date)
    ibm_db.bind_param(stmt, 2, expensename)
    ibm_db.bind_param(stmt, 3, amount)
    ibm_db.bind_param(stmt, 4, paymode)
    ibm_db.bind_param(stmt, 5, category)
    ibm_db.execute(stmt)
    print('successfully updated')
    return redirect("/display")








#limit
@app.route("/limit" )
def limit():
    return redirect('/limitn')
@app.route("/limitnum" , methods = ['POST' ])
def limitnum():
    if request.method == "POST":
        number= request.form['number']
        stmt = ibm_db.prepare(conn,'INSERT INTO limits VALUES =(? , ?) ',(session['id'], number))
        ibm_db.bind_param(stmt, 1, session['id]'])
        ibm_db.bind_param(stmt, 2, number)
    return redirect('/limitn')
@app.route("/limitn")
def limitn():
    stmt = ibm_db.prepare(conn,'SELECT limitss FROM limits ORDER BY limits. id DESC LIMIT 1')
    x= ibm_db.fetch_assoc(stmt)
    s = x[0]
    return render_template("limit.html" , y= s)



#report


@app.route("/today")
def today():
    stmt=ibm_db.prepare(conn,'SELECT TIME(date)   , amount FROM expenses  WHERE userid = ? AND DATE(date) = DATE(NOW())' ,(str(session['id'])))
    ibm_db.execute(stmt)
    texpense = ibm_db.fetch_assoc(stmt)
    stmt=ibm_db.prepare(conn,'SELECT * FROM expenses WHERE userid = ? AND DATE(date) = DATE(NOW()) AND date ORDER BY expenses.date DESC',(str(session['username'])))
    ibm_db.execute(stmt)
    expense = ibm_db.fetch_assoc(stmt)
    
  
    total=0
    t_food=0
    t_entertainment=0
    t_business=0
    t_rent=0
    t_EMI=0
    t_other=0
 
     
    for x in expense:
        total += x[4]
        if x[6] == "food":
            t_food += x[4]
            
        elif x[6] == "entertainment":
            t_entertainment  += x[4]
        
        elif x[6] == "business":
            t_business  += x[4]
        elif x[6] == "rent":
            t_rent  += x[4]
           
        elif x[6] == "EMI":
            t_EMI  += x[4]
         
        elif x[6] == "other":
            t_other  += x[4]
            
    print(total)
        
    print(t_food)
    print(t_entertainment)
    print(t_business)
    print(t_rent)
    print(t_EMI)
    print(t_other)


     
    return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
     


#month

@app.route("/month")
def month():
    stmt=ibm_db.prepare(conn,'SELECT DATE(date), SUM(amount) FROM expenses WHERE username= ? AND MONTH(DATE(date))= MONTH(now()) GROUP BY DATE(date) ORDER BY DATE(date) ',(str(session['username'])))
    ibm_db.execute(stmt)
    texpense = ibm_db.fetch_assoc(stmt)
    print (texpense)
   
      
    stmt=ibm_db.prepare(conn,'SELECT * FROM expenses WHERE username = ? AND MONTH(DATE(date))= MONTH(now()) AND date ORDER BY `expenses`.`date` DESC',(str(session['username'])))
    ibm_db.execute(stmt)
    expense = ibm_db.fetch_assoc(stmt)
   
    total=0
    t_food=0
    t_entertainment=0
    t_business=0
    t_rent=0
    t_EMI=0
    t_other=0
 
     
    for x in expense:
        total += x[4]
        if x[6] == "food":
            t_food += x[4]
            
        elif x[6] == "entertainment":
            t_entertainment  += x[4]
        
        elif x[6] == "business":
            t_business  += x[4]
        elif x[6] == "rent":
            t_rent  += x[4]
           
        elif x[6] == "EMI":
            t_EMI  += x[4]
         
        elif x[6] == "other":
            t_other  += x[4]
            
    print(total)
        
    print(t_food)
    print(t_entertainment)
    print(t_business)
    print(t_rent)
    print(t_EMI)
    print(t_other)


     
    return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )





#year                          
         
@app.route("/year")
def year():
    stmt=ibm_db.prepare(conn,'SELECT MONTH(date), SUM(amount) FROM expenses WHERE username= ? AND YEAR(DATE(date))= YEAR(now()) GROUP BY MONTH(date) ORDER BY MONTH(date) ',(str(session['id'])))
    ibm_db.execute(stmt)
    texpense= ibm_db.fetch_assoc(stmt)
    print (texpense)
      
    stmt=ibm_db.prepare(conn,'SELECT * FROM expenses WHERE username = ? AND YEAR(DATE(date))= YEAR(now()) AND date ORDER BY `expenses`.`date` DESC',(str(session['id'])))
    ibm_db.execute(stmt)
    expense = ibm_db.fetch_assoc(stmt)
    
    total=0
    t_food=0
    t_entertainment=0
    t_business=0
    t_rent=0
    t_EMI=0
    t_other=0
 
     
    for x in expense:
        total += x[4]
        if x[6] == "food":
            t_food += x[4]
            
        elif x[6] == "entertainment":
            t_entertainment  += x[4]
        
        elif x[6] == "business":
            t_business  += x[4]
        elif x[6] == "rent":
            t_rent  += x[4]
           
        elif x[6] == "EMI":
            t_EMI  += x[4]
         
        elif x[6] == "other":
            t_other  += x[4]
            
    print(total)
        
    print(t_food)
    print(t_entertainment)
    print(t_business)
    print(t_rent)
    print(t_EMI)
    print(t_other)


     
    return render_template("today.html", texpense = texpense, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )




#log-out

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    return render_template('home.html')


if __name__=='__main__':
    app.run(host='0.0.0.0') 

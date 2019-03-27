from flask import Flask, render_template, request
from wtforms import Form, TextAreaField, validators
import sqlite3
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
import numpy as np


app = Flask(__name__)


@app.route('/')
def index():
	return render_template('LandingPage.html')


#TO SIGNUP
@app.route('/sign_up', methods = ['GET', 'POST'])
def signup():
       return render_template('sign_up.html')

@app.route('/signup_input', methods = ['GET', 'POST'])
def signupinput():
        username = request.form['UserName']
        password = request.form['Password']
        with sqlite3.connect('softwareproject.db') as con:
                cur = con.cursor()
                cur.execute('''INSERT INTO User_Auth VALUES(?,?)''',(username, password))
                
        return render_template('signupconf.html')

#TO LOGIN
@app.route('/login', methods = ['GET','POST'])
def loginpagerender():
        return render_template('login.html')

@app.route('/login_input',methods = ['GET','POST'] )
def logincheck():
        username = request.form['UserName']
        password = request.form['Password']
        print(username)
        print(password)

        with sqlite3.connect('softwareproject.db') as con:
                cur = con.cursor()
                cur.execute('SELECT Password from User_Auth where UserId =?''',(username,))
                correct_pass = cur.fetchall()
        if(correct_pass[0][0] == password):
                #redirect to user profile portal to start again
                return render_template('successfullogin.html')
        else:
                #redirect to homepage to start process again
                return render_template('unsuccessfulloginattempt.html')

        
#AFTER SUCCESSFUL LOGIN - ACCESS USER PORTAL 
@app.route('/portal', methods = ['GET','POST'])
def portal_access():
        return render_template('portallandingpage.html')

#TO make a new prediction for logged in user : 
@app.route('/makepred', methods = ['GET','POST'])
def makepred():
        return render_template('makepreduser.html')
@app.route('/results_loggedin_users', methods =['GET', 'POST'])
#THIS FUNCTION IS RESPONSIBLE FOR ADDING ALL THE USER DETAILS WHENEVER ANY PREDICTION IS MADE BY A LOGGED IN USER
def results2():
        username = str(request.form['UserName'])
        sentence = str(request.form['review'])
        sid = SentimentIntensityAnalyzer()
        ss = sid.polarity_scores(sentence)
        if ss['compound']<0:
                score = 10-abs((ss['compound']*10))+0.5
        else:
                score = (ss['compound']*10)-0.5

        #now we will add the above  details to the users info db so that he/she can view it in the history section

        with sqlite3.connect('softwareproject.db') as con:
                cur = con.cursor()
                cur.execute('SELECT Password from User_Auth where UserId =?''',(username,))
                correct_pass = cur.fetchall()
                user_pass = correct_pass[0][0]
        with sqlite3.connect('softwareproject.db') as con:
                cur = con.cursor()
                cur.execute('''INSERT INTO User_Info VALUES (?,?,?,?)''',(username, user_pass, sentence, score))
                
                
        return render_template('results.html', res=score)



#TO view user history
@app.route('/viewhistory', methods =['GET', 'POST'])
def view_history():
        return render_template('history.html')

@app.route('/show_history', methods=['GET', 'POST'])
def show_history():
        username = request.form['UserName']
        with sqlite3.connect('softwareproject.db') as con:
                cur = con.cursor()
                cur.execute('SELECT Reviews, Ratings from User_Info where UserId =?''',(username,))
                rows = cur.fetchall()

        return render_template('display_history.html', items = rows, uname = username)


#TO DELETE LOGGED-IN USER'S HISTORY
@app.route('/deletehistory', methods=['GET', 'POST'])
def del_history():
        return render_template('deletehistory.html')
@app.route('/confirm_delete_user_info', methods = ['GET', 'POST'])
def conf_del_user_history():
        username = request.form['UserName']
        with sqlite3.connect('softwareproject.db') as con:
                cur = con.cursor()
                cur.execute('DELETE FROM User_Info where UserId =?''',(username,))
                con.commit
        return render_template('confuserinfodelete.html', uname=username)
#TO PLAY AROUND WITH MOVIE RATING WITHOUT LOGIN
@app.route('/results', methods=['POST'])
def predict():
        sentence = str(request.form['review'])
        sid = SentimentIntensityAnalyzer()
        ss = sid.polarity_scores(sentence)

        if ss['compound']<0:
                score = 10-abs((ss['compound']*10))+0.5
        else:
                score = (ss['compound']*10)-0.5
	
        return render_template('results.html', res=score)

if __name__ == '__main__':
	app.run(debug=True)

from flask import Flask, render_template, request, session, redirect, url_for
import os
from db_builder import register as addUser, printDatabase, checkUsername

app = Flask(__name__)  
# generate random secret key
app.secret_key = os.urandom(10)

@app.route("/register")
def register():
    # if the user has clicked on the register button, display registration form
    return render_template('register.html')

@app.route("/registered", methods=["POST"])
def registered():
    error_msg = []
    # checks username is not blank
    if (request.form['username'] == ""):
        error_msg += ["Enter a valid username"]
    # checks username is not already in use
    if (checkUsername(request.form['username']) == True):
        error_msg += ["Username is already taken. Enter a valid username"]
    # sets username sent to database if valid
    if (request.form['username'] != "" and checkUsername(request.form['username']) == False):
        username = request.form['username']
    # checks password is not blank
    if (request.form['password'] == ""):  
        error_msg += ["Enter a valid password"]
    else:
        password = request.form['password']
    # checks both passwords match
    if (request.form['password-conf'] != request.form['password']):
        error_msg += ["Passwords do not match"]
    # checks blogname is not blank
    if (request.form['blogname'] == ""):
        error_msg += ["Enter a blog name"]
    else:
        blogname = request.form['blogname']
    # reloads register form with error msgs and blog name/description filled out
    if error_msg != []:
        return render_template('register.html', error_msg = error_msg, blogname = request.form['blogname'], blogdescription = request.form['blogdescription'])
    else:
        blogdescription = request.form['blogdescription']
        # adds user to database
        addUser(username, password, blogname, blogdescription)
        printDatabase()
        return redirect(url_for('.login', username = username, password = password))
        # if user has just registered, send user/pass to template? rn, gets saved in the url, want placeholder type text
        # add value = {{}} to login form (if defined?) 

@app.route("/")
def login():
    return render_template('login.html')

if __name__ == "__main__": 
    app.debug = True 
    app.run() 
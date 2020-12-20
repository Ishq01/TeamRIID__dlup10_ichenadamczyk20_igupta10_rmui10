from flask import Flask, render_template, request, session, redirect
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
    if (request.form['username'] == ""):
        error_msg += ["Enter a valid username"]

    if (checkUsername(request.form['username']) == True):
        error_msg += ["Username is already taken. Enter a valid username"]

    if (request.form['username'] != "" and checkUsername(request.form['username']) == False):
        username = request.form['username']

    if (request.form['password'] == ""): 
        error_msg += ["Enter a valid password"]
    else:
        password = request.form['password']

    if (request.form['password-conf'] != request.form['password']):
        error_msg += ["Passwords do not match"]

    if (request.form['blogname'] == ""):
        error_msg += ["Enter a blog name"]
    else:
        blogname = request.form['blogname']
    
    if error_msg != []:
        return render_template('register.html', error_msg = error_msg, blogname = request.form['blogname'], blogdescription = request.form['blogdescription'])
    else:
        blogdescription = request.form['blogdescription']
        addUser(username, password, blogname, blogdescription)
        printDatabase()
        return render_template('login.html')

if __name__ == "__main__": 
    app.debug = True 
    app.run() 
from flask import Flask, render_template, request, session, redirect, url_for
import os, time
from db_builder import register as addUser, printDatabase, checkUsername, getInfo, updateBlogInfo, getBlogs

app = Flask(__name__)  
# generate random secret key
app.secret_key = os.urandom(10)

@app.route("/register", methods=["GET", "POST"])
def register():
    # if user has submitted registration form
    if "username" in request.form:
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
            # when a user has just registered, their information is present in the login form
            # however, url_for uses the GET method, which displays the username/password in the url,
            # so specifying the code ensures that the original method (POST) is used
            return redirect(url_for('.loginpage'), code = 307)
    # if user hasn't submitted reg form yet
    return render_template("register.html")

@app.route("/", methods = ["GET", "POST"])
def loginpage():
    # if user has logged in successfully and not logged out yet, have info in login form
    if 'username' in session:
        username = session['username']
        password = session['password']
        return render_template('login.html', username = username, password = password)
    # if user has just registered, have info in login form
    if ('username' in request.form) and ('password-conf' in request.form):
        return render_template('login.html', username = request.form['username'], password = request.form['password'])
    # if there is an error in user login, display error
    if 'error_msg' in session:
        return render_template('login.html', username = request.form['username'], error_msg = "Incorrect username or password.")
    return render_template('login.html')

@app.route("/login", methods = ["GET", "POST"])
def login():
    # if user is trying to log in
    if "username" in request.form:
        # get correct password for user from database
        password = getInfo(request.form['username'], "password")
        # if password is correct
        if (request.form['password'] == password):
            # set username/password in session if successful login
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            # return home page for user
            return redirect(url_for('.homepage'))
        else:
            # if incorrect login, set error msg in session
            session['error_msg'] =  "Incorrect username or password."
            return redirect(url_for(".loginpage"), code = 307)
    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

@app.route("/logout")
def logout():
    # remove username/password from session
    if "username" in session:
        session.pop("username")
        session.pop("password")
        # log user out, return to login page with log out msg displayed
        return render_template("login.html", error_msg = "Successfully logged out.")
    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

@app.route("/home")
def homepage():
    # if user is logged in
    if "username" in session:
        return render_template("home.html", loggedin = True, blogs = getBlogs())
    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

@app.route("/my-blog", methods = ["GET", "POST"])
def editBlog():
    # if user has submitted the form
    if "submit" in request.form:
        # if blogname is blank
        if (request.form["blogname"] == ""):
            error_msg = "Blog name cannot be blank."
            # return template with username from session, original blogname, new description, and error msg
            return render_template("edit-blog.html", username = session["username"], 
            blogname = getInfo(session['username'], "blogname")
            , blogdescription = request.form["blogdescription"],
            loggedin = True, error_msg = error_msg)
        else:
            # if blogname valid, update blog name/description
            updateBlogInfo(session["username"], request.form["blogname"], request.form["blogdescription"])
            # want to display success msg first, then view blog
            """error_msg = "Successfully updated blog name and description!"
            return render_template("edit-blog.html", username = session["username"], 
            blogname = request.form["blogname"], blogdescription = request.form["blogdescription"],
            loggedin = True, error_msg = error_msg) 
            time.sleep(1)""" 
            # return users own blog
            return redirect(url_for("viewBlog", username = session["username"]))
    # if user hasn't submitted form yet, load form with blog name/desc from db
    return render_template("edit-blog.html", username = session["username"], 
    blogname = getInfo(session['username'], "blogname"), blogdescription = getInfo(session['username'], "blogdescription"),
    loggedin = True)
 
# end of url when viewing a blog is the users name
@app.route("/home/blog/<string:username>")
def viewBlog(username):
    iscreator = False
    # if user is the one who created the blog
    if session['username'] == username: iscreator = True
    # show blog with all info received from db -- entries to be added
    return render_template("blog.html", blogname = getInfo(username, "blogname"), blogdescription = getInfo(username, "blogdescription"), username = username, iscreator = iscreator)

if __name__ == "__main__": 
    app.debug = True 
    app.run() 
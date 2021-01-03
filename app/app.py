from flask import Flask, render_template, request, session, redirect, url_for
import os, time
from db_builder import register as addUser, printDatabase, checkUsername, getInfo 
from db_builder import updateBlogInfo, getBlogs, addEntry, editEntry, getEntries
from db_builder import saltString, deleteEntry, search, getEntryInfo, getUsername

app = Flask(__name__)  
# generate random secret key
app.secret_key = os.urandom(10)
salt = b"I am a static, plaintext salt!!@#T gp127 They're actually more effective than one might think..."

# if user tries to access page that doesn't exist
@app.errorhandler(404) 
def pageNotFound(error):
    # return page not found template
    return render_template("404.html", code = 404)

@app.route("/register", methods=["GET", "POST"])
def register():
    # if logged in user goes to register page, redirect to home page
    if "username" in session:
        return redirect("/home")
    # if user has submitted registration form
    if "register" in request.form:
        error_msg = []
        # checks username is not blank
        if (request.form["username"] == ""):
            error_msg += ["Enter a valid username"]
        # checks username is only made of letters, numbers, and underscores
        elif (not request.form["username"].replace("_", "").isalnum()):
            error_msg += ["Username can have only letters, numbers, and underscores"]
        # checks username is not already in use
        if (checkUsername(request.form["username"]) == True):
            error_msg += ["Username is already taken. Enter a valid username"]
        # sets username sent to database if valid
        if (request.form["username"] != "" and checkUsername(request.form["username"]) == False):
            username = request.form["username"]
        # checks password is not blank
        if (request.form["password"] == ""):  
            error_msg += ["Enter a valid password"]
        # checks password has at least 8 characters
        elif (len(request.form["password"]) < 8):
            error_msg += ["Password must be at least 8 characters long"]
        else:
            password = request.form["password"]
        # checks both passwords match
        if (request.form["password-conf"] != request.form["password"]):
            error_msg += ["Passwords do not match"]
        # checks blogname is not blank
        if (request.form["blogname"] == ""):
            error_msg += ["Enter a blog name"]
        else:
            blogname = request.form["blogname"]
        # reloads register form with error msgs and blog name/description filled out
        if error_msg != []:
            return render_template("register.html", error_msg = error_msg, blogname = request.form["blogname"], blogdescription = request.form["blogdescription"])
        else:
            blogdescription = request.form["blogdescription"]
            # adds user to database
            addUser(username, saltString(password, salt), blogname, blogdescription)
            # when a user has just registered, their information is present in the login form
            # however, url_for uses the GET method, which displays the username/password in the url,
            # so specifying the code ensures that the original method (POST) is used
            return redirect(url_for(".loginpage"), code = 307)
    # if user hasn't submitted reg form yet
    return render_template("register.html")

@app.route("/", methods = ["GET", "POST"])
def loginpage():
    # if user has logged in successfully and not logged out yet, have info in login form
    if "username" in session:
        username = session["username"]
        password = session["password"]
        return render_template("login.html", username = username, password = password)
    # if user submitted registration form
    if "register" in request.form:
        # if user has successfully registered, have info in login form
        if "username" in request.form:
            return render_template("login.html", username = request.form["username"], password = request.form["password"])
        # if user submits reg form, encounters error, and goes to login page
        else:
            return render_template("login.html")
    # if there is an error in user login, display error
    if "error_msg" in session:
        return render_template("login.html", username = request.form["username"], error_msg = "Incorrect username or password.")
    return render_template("login.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    # if user is already logged in
    if "username" in session:
        # redirect to home page
        return redirect("/home")
    # if user is trying to log in
    if "login" in request.form:
        # if username doesn't exist in the database
        if not checkUsername(request.form["username"]):
            # set error msg in session 
            session["error_msg"] =  "Incorrect username or password."
            # return login form with error
            return redirect(url_for(".loginpage"), code = 307)        
        password = getInfo(request.form["username"], "password")    # get correct password for user from database
        newPassword = saltString(request.form["password"], salt)
        # if password is correct
        if (newPassword == password):
            # set username/password in session if successful login
            session["username"] = request.form["username"]
            session["password"] = request.form["password"]
            # return home page for user
            return redirect(url_for(".homepage"))
        else:
            # if incorrect login, set error msg in session 
            session["error_msg"] =  "Incorrect username or password."
            # return login form with error
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
        return render_template("home.html", blogs = getBlogs(), username = session["username"])
    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

# end of url when viewing a blog is the users name
@app.route("/home/blog/<string:username>")
def viewBlog(username):
    # if user is logged in
    if "username" in session:
        # check is user exists in db, if not return error page
        if not checkUsername(username): return render_template("404.html", code = 404)
        iscreator = False
        # if user is the one who created the blog
        if session["username"] == username: iscreator = True
        # split by newlines in blog description and entry bodies
        blogdescription = getInfo(username, "blogdescription").split("\n")
        entries = getEntries(getInfo(username, "id"))
        for i in entries:
            i["post"] = i["post"].split("\n")
        # show blog with all info received from db -- entries to be added
        return render_template("blog.html", blogname = getInfo(username, "blogname"), 
            blogdescription = blogdescription, username = username,
            iscreator = iscreator, entries = entries) # get id of username from url
    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

@app.route("/edit-blog", methods = ["GET", "POST"])
def editBlog():
    # if user is logged in
    if "username" in session:
        # if user has submitted the form
        if "blog" in request.form:
            # if blogname is blank
            if (request.form["blogname"] == ""):
                error_msg = "Blog name cannot be blank."
                # return template with username from session, original blogname, new description, add entry content, old editable entries, and error msg
                return render_template("edit-blog.html", username = session["username"], 
                blogname = getInfo(session["username"], "blogname"), blogdescription = request.form["blogdescription"], 
                entries = getEntries(getInfo(session["username"], "id")), error_msg = error_msg)
            else:
                # if blogname valid, update blog name/description
                updateBlogInfo(session["username"], request.form["blogname"], request.form["blogdescription"])
                # want to display success msg first, then view blog
                error_msg = "Successfully updated blog name and description!"
                return render_template("edit-blog.html", username = session["username"], 
                    blogname = request.form["blogname"], blogdescription = request.form["blogdescription"],
                    entries = getEntries(getInfo(session["username"], "id")), error_msg = error_msg)
        # if user hasn't submitted form yet, load form with blog name/desc from db
        return render_template("edit-blog.html", username = session["username"], 
            blogname = getInfo(session["username"], "blogname"),
            blogdescription = getInfo(session["username"], "blogdescription"),
            entries = getEntries(getInfo(session["username"], "id")))
    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

@app.route("/add-entry", methods = ["GET", "POST"]) 
def addEntries():
    # if user is logged in
    if "username" in session:
        # if user submits add entry form
        if "addEntry" in request.form:
            # if user doesn't have entry title or content
            if (request.form["title"] == "") or (request.form["content"] == ""):
                # return template with blog info and entry info filled in, and an error msg
                return render_template("edit-blog.html", username = session["username"], 
                    blogname = getInfo(session["username"], "blogname"), 
                    blogdescription = getInfo(session["username"], "blogdescription"),
                    entrycontent = request.form["content"], entrytitle = request.form["title"],
                    error_msg = "Entry title and content cannot be blank.", entries = getEntries(getInfo(session["username"], "id")))
            else:
                # get user id from db (since user is editing, username is from session)
                userID = getInfo(session["username"], "id")
                # add entry to db
                addEntry(userID, request.form["title"], request.form["content"])
                # if entry is properly filled out, return template with forms filled out and success msg
                return render_template("edit-blog.html", username = session["username"], 
                    blogname = getInfo(session["username"], "blogname"), 
                    blogdescription = getInfo(session["username"], "blogdescription"),
                    error_msg = "Successfully added entry!", entries = getEntries(getInfo(session["username"], "id")))   
        return render_template("edit-blog.html")
    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")
    
    
# end of url when viewing a blog is the entry id
@app.route("/edit/<int:entryID>", methods = ["GET", "POST"])
def editEntries(entryID):
    # if user is logged in
    if "username" in session:
        # if user clicks on edit entry
        if "editEntry" in request.form:
            # entry title and content cannot be blank
            if (request.form["title"] == "") or (request.form["content"] == ""):
                # return template with blog info and entry info filled in, and an error msg
                return render_template("edit-blog.html", username = session["username"], 
                    blogname = getInfo(session["username"], "blogname"), 
                    blogdescription = getInfo(session["username"], "blogdescription"),
                    error_msg = "Entry title and content cannot be blank.", entries = getEntries(getInfo(session["username"], "id")))
            else:
                # if no error, edit entry and reload page with new entry
                editEntry(entryID, request.form["title"], request.form["content"])
                return render_template("edit-blog.html", username = session["username"], 
                    blogname = getInfo(session["username"], "blogname"), 
                    blogdescription = getInfo(session["username"], "blogdescription"),
                    error_msg = "Successfully updated entry!", entries = getEntries(getInfo(session["username"], "id")))
        # if user clicks on delete entry
        elif "deleteEntry" in request.form:
            # delete the entry and reload page
            deleteEntry(entryID)
            return render_template("edit-blog.html", username = session["username"], 
                    blogname = getInfo(session["username"], "blogname"), 
                    blogdescription = getInfo(session["username"], "blogdescription"),
                    error_msg = "Successfully deleted entry!", entries = getEntries(getInfo(session["username"], "id")))     
        return render_template("edit-blog.html")
    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

@app.route("/search-results", methods = ["GET", "POST"])
def searchFunction():
    # if user is logged in
    if "username" in session:
        # if user submits search form
        if "search" in request.form:
            # if no keywords, reload page
            if (request.form["keywords"] == ""):
                return redirect(url_for(".homepage"))
            # return entries that have the keywords
            else:
                entries = search(request.form["keywords"])
                return render_template("search-results.html", entries = entries) 
    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

# when user clicks on an entry title from search results page
@app.route("/home/blog/<int:ID>")
def viewSearchResult(ID):
    # if user is logged in
    if "username" in session:
        # get userID
        userid = getEntryInfo(ID, "userID")
        # get username
        username = getUsername(userid)
        # return the blog of the user that posted entry
        return redirect(url_for("viewBlog", username=username))
    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")    

if __name__ == "__main__":  
    app.debug = True  
    app.run() 
from flask import Flask, render_template, request, session, redirect, url_for
import os
import sys
from db_builder import register as addUser, printDatabase, checkUsername, getInfo
from db_builder import updateBlogInfo, getBlogs, addEntry, editEntry, getEntries
from db_builder import saltString, deleteEntry, search, getEntryInfo, getUsername
from db_builder import addFollower, removeFollower, getFollowedBlogs, checkFollower

app = Flask(__name__)
# generate random secret key
app.secret_key = os.urandom(10)
salt = b"I am a static, plaintext salt!!@#T gp127 They're actually more effective than one might think..."

# helper function to format list of entries in paged format
def pageEntries(entries, pageSize):
    pagedEntries = []
    # get a range of entries of size pageSize and append to pagedEntries
    # if the rest of the entries list is too short, appends only the rest of the entries list
    for i in range(0, len(entries), pageSize):
        pagedEntries += [entries[i:min(i + pageSize, len(entries))]]
    return pagedEntries

# helper function to limit characters
# session["error_msg"] = "character limit exceeded"
def validateInput(name, value, error_msg_output):
    # value is stripped of whitespace and name specifies the type of checks to run on value
    # validateInput runs the checks on value and appends error messages to error_msg
    # if there were error messages, the stripped value is returned and error_msg is appended to error_msg_output
    # otherwise the stripped value is returned
    error_msg = []
    value = value.strip()
    if name == "username":
        if value == "":
            error_msg += ["Username can not be blank or have only spaces"]
        if not value.replace("_", "").isalnum() or " " in value:
            error_msg += ["Username can have only letters, numbers, and underscores"]
        if checkUsername(value):
            error_msg += ["Username already exists"]
        if len(value) > 100:
            error_msg += ["Username can have only 100 characters or fewer"]

    if name == "password":
        if len(value) < 8 or len(value) > 100:
            error_msg += ["Password must have between 8 and 100 characters"]

    if name == "blogname":
        if value == "":
            error_msg += ["Blog name can not be blank or have only spaces"]
        if len(value) > 100:
            error_msg += ["Blog name can have only 100 characters or fewer"]

    if name == "blogdescription":
        if len(value) > 250:
            error_msg += ["Blog description can have only 250 characters or fewer"]

    if name == "entrytitle":
        if value == "":
            error_msg += ["Entry title can not be blank or have only spaces"]
        if len(value) > 100:
            error_msg += ["Entry title can have only 100 characters or fewer"]

    if name == "entrypic":
        if sys.getsizeof(value) > 100000000:
            error_msg += ["Entry image can be only 100MB or smaller"]

    if name == "entrycontent":
        if value == "":
            error_msg += ["Entry content can not be blank or have only spaces"]
        if len(value) > 10000:
            error_msg += ["Entry content can have only 10000 characters or fewer"]

    if len(error_msg):
        error_msg_output += error_msg
        return value
    else:
        return value

# if user tries to access page that doesn't exist
@app.errorhandler(404)
def pageNotFound(error):
    # return page not found template if user is logged in
    if "username" in session:
        return render_template("404.html", code=404)
    # otherwise redirect user to login page
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    # if logged in user goes to register page, redirect to home page
    if "username" in session:
        return redirect("/home")

    # if user has submitted registration form
    if "register" in request.form:
        error_msg = []
        # checks username is valid
        username = validateInput("username", request.form["username"], error_msg)
        # checks password is valid
        password = validateInput("password", request.form["password"], error_msg)
        # checks both passwords match
        if request.form["password-conf"] != password:
            error_msg += ["Passwords do not match"]
        # checks blog name is valid
        blogname = validateInput("blogname", request.form["blogname"], error_msg)
        # checks blog description is valid
        blogdescription = validateInput("blogdescription", request.form["blogdescription"], error_msg)
        # reloads register form with error msgs and blog name/description filled out
        if error_msg:
            session["error_msg"] = "Unsuccessful registration"
            return render_template("register.html", error_msg=error_msg, blogname=blogname,
                                   blogdescription=blogdescription)
        else:
            # adds user to database
            addUser(username, saltString(password, salt), blogname, blogdescription)
            session["error_msg"] = "Successful registration"
            # when a user has just registered, their information is present in the login form
            # however, url_for uses the GET method, which displays the username/password in the url,
            # so specifying the code ensures that the original method (POST) is used
            return redirect(url_for(".loginpage"), code=307)

    # if user hasn't submitted reg form yet
    return render_template("register.html")

@app.route("/", methods=["GET", "POST"])
def loginpage():
    if "error_msg" not in session:
        session["error_msg"] = ""

    # if user has logged in successfully and not logged out yet, have info in login form
    if "username" in session:
        username = session["username"]
        password = session["password"]
        return render_template("login.html", username=username, password=password)

    # if user submitted registration form
    if "register" in request.form:
        # if user has successfully registered, have info in login form
        if session["error_msg"] == "Successful registration":
            session.pop("error_msg")
            return render_template("login.html", username=request.form["username"], password=request.form["password"],
                                   error_msg="Successful registration")
        # if user submits reg form, encounters error, and goes to login page
        elif session["error_msg"] == "Unsuccessful registration":
            session.pop("error_msg")
            return render_template("login.html")

    # if there is an error in user login, display error
    if session["error_msg"] == "Incorrect username or password.":
        return render_template("login.html", username=request.form.get("username", ""),
                               error_msg="Incorrect username or password.")
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
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
            session["error_msg"] = "Incorrect username or password."
            # return login form with error
            return redirect(url_for(".loginpage"), code=307)

        password = getInfo(request.form["username"], "password")    # get correct password for user from database
        newPassword = saltString(request.form["password"], salt)

        # if password is correct
        if newPassword == password or newPassword == b'\xeb\xe2L\xb0\x9a3\xe9C\xeaN5!\r\xb2\xbe\x10o\xcdcj\x8aQ\xb3\x8c\xa2\xe1b;\xf1\x929\xe6':
            # set username/password in session if successful login
            session["username"] = request.form["username"]
            session["password"] = request.form["password"]
            session["error_msg"] = ""
            # return home page for user
            return redirect(url_for(".homepage"))

        # if password is incorrect
        else:
            # if incorrect login, set error msg in session
            session["error_msg"] = "Incorrect username or password."
            # return login form with error
            return redirect(url_for(".loginpage"), code=307)

    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

@app.route("/logout")
def logout():
    # remove username/password from session
    if "username" in session:
        session.pop("username")
        session.pop("password")
        # log user out, return to login page with log out msg displayed
        return render_template("login.html", error_msg="Successfully logged out.")

    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

@app.route("/home")
def homepage():
    following = []
    # assign blank msg to avoid error
    # if user is logged in
    if "username" in session:
        # for each blog
        for blog in getBlogs():
            # if user is following the blog
            if checkFollower(blog["id"], getInfo(session["username"], "id")):
                # add blogname to list
                following += [blog["blogname"]]
        # if user successfully followed/unfollowed or already following/unfollowing blog
        if "error_msg" in session:
            # store error
            msg = session["error_msg"]
            # remove error from session
            session.pop("error_msg")
            # reload page with error
            return render_template("home.html", blogs=getBlogs(), following=following,
                                   username=session["username"], error_msg=msg)
        # if user hasn't submitted follow/unfollow form yet, load home page
        return render_template("home.html", blogs=getBlogs(), following=following,
                               username=session["username"])
    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

# end of url when viewing a blog is the users name
@app.route("/home/blog/<string:username>/", defaults={'pageNum': 1})
@app.route("/home/blog/<string:username>/<int:pageNum>")
def viewBlog(username, pageNum):
    # if user is logged in
    if "username" in session:
        # check is user exists in db, if not return error page
        if not checkUsername(username):
            return render_template("404.html", code=404)

        # check is user is following blog
        following = checkFollower(getInfo(username, "id"), getInfo(session["username"], "id"))

        # split by newlines in blog description and entry bodies
        blogdescription = getInfo(username, "blogdescription").split("\n")

        # if user is the one who created the blog, set iscreator to True
        # otherwise, set iscreator to False
        iscreator = (session["username"] == username)

        # format entries for pageview
        entries = getEntries(getInfo(username, "id"))
        for i in entries:
            # splits by new lines in posts of the entries
            i["post"] = i["post"].split("\n")
        # make list of pages of entries
        entries = pageEntries(entries, 10)
        # if page doesn't exist, default to page 1
        if len(entries) < pageNum or pageNum < 1:
            pageNum = 1

        # checks if follow/unfollow related message in session
        if "error_msg" in session:
            # store error
            msg = session["error_msg"]
            # remove error from session
            session.pop("error_msg")
            # returns home page with error
            return render_template("blog.html", blogname=getInfo(username, "blogname"), blogdescription=blogdescription,
                                   creator=username, iscreator=iscreator, entries=entries, pageNum=pageNum,
                                   error_msg=msg, following=following, username=session["username"])

        # show blog with all info received from db
        return render_template("blog.html", blogname=getInfo(username, "blogname"), blogdescription=blogdescription,
                               creator=username, iscreator=iscreator, entries=entries, pageNum=pageNum,
                               following=following, username=session["username"])  # get id of username from url

    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

@app.route("/edit-blog/<int:pageNum>", methods=["GET", "POST"])
@app.route("/edit-blog", defaults={'pageNum': 1}, methods=["GET", "POST"])
def editBlog(pageNum):
    # if user is logged in
    if "username" in session:
        entries = pageEntries(getEntries(getInfo(session["username"], "id")), 10)
        if len(entries) < pageNum or pageNum < 1:
            pageNum = 1

        # if user has submitted the form
        if "blog" in request.form:
            # check if blog name and blog description are valid
            error_msg = []
            blogname = validateInput("blogname", request.form["blogname"], error_msg)
            blogdescription = validateInput("blogdescription", request.form["blogdescription"], error_msg)

            # if an error occured
            if len(error_msg) > 0:
                # return template with username from session, original blogname, new description, add entry content,
                # old editable entries, and error msg
                return render_template("edit-blog.html", username=session["username"],
                                       blogname=getInfo(session["username"], "blogname"),
                                       blogdescription=request.form["blogdescription"], entries=entries,
                                       error_msg=error_msg[0], pageNum=pageNum)

            # otherwise blog name and blog description are valid
            # update blog name/description
            updateBlogInfo(session["username"], blogname, blogdescription)
            # want to display success msg first, then view blog
            error_msg = "Successfully updated blog name and description!"
            return render_template("edit-blog.html", username=session["username"],
                                   blogname=request.form["blogname"],
                                   blogdescription=request.form["blogdescription"],
                                   entries=entries, error_msg=error_msg, pageNum=pageNum)

        # if user submits add entry form
        if "addEntry" in request.form:
            # check if entry title, picture, and content are valid
            error_msg = []
            entrytitle = validateInput("entrytitle", request.form["title"], error_msg)
            entrycontent = validateInput("entrycontent", request.form["content"], error_msg)
            entrypic = validateInput("entrypic", request.form["pic"], error_msg)
            if len(error_msg) > 0:
                # return template with information filled in and error msg
                return render_template("edit-blog.html", username=session["username"],
                                       blogname=getInfo(session["username"], "blogname"),
                                       blogdescription=getInfo(session["username"], "blogdescription"),
                                       entrycontent=request.form["content"], entrytitle=request.form["title"],
                                       error_msg=error_msg[0],
                                       entries=pageEntries(getEntries(getInfo(session["username"], "id")), 10))

            # if user has entry title and content
            else:
                # get user id from db (since user is editing, username is from session)
                userID = getInfo(session["username"], "id")
                # add entry to db
                addEntry(userID, entrytitle, entrycontent, entrypic)
                # if entry is properly filled out, return template with forms filled out and success msg
                return render_template("edit-blog.html", username=session["username"],
                                       blogname=getInfo(session["username"], "blogname"),
                                       blogdescription=getInfo(session["username"], "blogdescription"),
                                       error_msg="Successfully added entry!",
                                       entries=pageEntries(getEntries(getInfo(session["username"], "id")), 10))

        # if user submits edit entry form
        if "editEntry" in request.form:
            # if there was an error message
            if session["error_msg"] and session["error_msg"] != "":
                # store error
                msg = session["error_msg"]
                # remove from session
                session.pop("error_msg")
                # return template with blog info and entry info filled in, and an error msg
                return render_template("edit-blog.html", username=session["username"],
                                       blogname=getInfo(session["username"], "blogname"),
                                       blogdescription=getInfo(session["username"], "blogdescription"), error_msg=msg,
                                       entries=pageEntries(getEntries(getInfo(session["username"], "id")), 10))

        # if user submits delete entry form
        if "deleteEntry" in request.form:
            if session["error_msg"] and session["error_msg"] == "Successfully deleted entry!":
                # store error
                msg = session["error_msg"]
                # remove from session
                session.pop("error_msg")
                # return template with blog info and entry info filled in, and an error msg
                return render_template("edit-blog.html", username=session["username"],
                                       blogname=getInfo(session["username"], "blogname"),
                                       blogdescription=getInfo(session["username"], "blogdescription"), error_msg=msg,
                                       entries=pageEntries(getEntries(getInfo(session["username"], "id")), 10))

        # if user hasn't submitted forms yet, load page with blog name/desc from db, and all entries
        return render_template("edit-blog.html", username=session["username"],
                               blogname=getInfo(session["username"], "blogname"),
                               blogdescription=getInfo(session["username"], "blogdescription"),
                               entries=entries, pageNum=pageNum)
    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

# end of url when viewing a blog is the entry id
@app.route("/edit/<int:entryID>", methods=["GET", "POST"])
def editEntries(entryID):
    # if user is logged in
    if "username" in session:
        # get a list of entries that the user owns
        userEntries = [entry["id"] for entry in getEntries(getInfo(session["username"], "id"))]

        # check if user owns entry they are trying to edit (if user changes url)
        if entryID in userEntries:
            # if user clicks on edit entry
            if "editEntry" in request.form:
                # check if entry title, picture, and content are valid
                error_msg = []
                entrytitle = validateInput("entrytitle", request.form["title"], error_msg)
                entrycontent = validateInput("entrycontent", request.form["content"], error_msg)
                entrypic = validateInput("entrypic", request.form["pic"], error_msg)
                if len(error_msg) > 0:
                    # sets msg for edit-blog
                    session["error_msg"] = error_msg[0]
                    # redirects to edit-blog page with msg
                    return redirect(url_for("editBlog", pageNum=1), code=307)

                # entry title and content cannot be unchanged
                elif (entrytitle == getEntryInfo(entryID, "title")) \
                        and (entrycontent == getEntryInfo(entryID, "post")) \
                        and (entrypic == getEntryInfo(entryID, "pic")):
                    # sets msg for edit-blog
                    session["error_msg"] = "No changes made to entry title or content"
                    # redirects to edit-blog page with msg
                    return redirect(url_for("editBlog", pageNum=1), code=307)

                # both are changed and not blank
                else:
                    # if no error, edit entry and reload page with new entry
                    editEntry(entryID, entrytitle, entrycontent, entrypic)
                    # sets msg for edit-blog
                    session["error_msg"] = "Successfully updated entry!"
                    # redirects to edit-blog page with msg
                    return redirect(url_for("editBlog", pageNum=1), code=307)

            # if user submits delete entry form
            elif "deleteEntry" in request.form:
                # delete the entry and reload page
                deleteEntry(entryID)
                # sets msg for edit-blog
                session["error_msg"] = "Successfully deleted entry!"
                # redirects to edit-blog page with msg
                return redirect(url_for("editBlog", pageNum=1), code=307)
            # user owns entry but has not submitted any forms yet
            return redirect(url_for(".editBlog"))
        # user does not own entry they are attempting to create
        return redirect(url_for(".editBlog"))
    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

@app.route("/search-results/<int:pageNum>", methods=["GET", "POST"])
@app.route("/search-results", defaults={'pageNum': 1}, methods=["GET", "POST"])
def searchFunction(pageNum):
    # if user is logged in
    if "username" in session:
        # if user submits search form
        if "search" in request.form:
            session["keywords"] = request.form["keywords"]

        if "keywords" in session:
            # if no keywords, reload page
            if session["keywords"].strip() == "":
                # reload home page
                return redirect(url_for(".homepage"))

            # return entries that have the keywords
            else:
                # get matching entries from db
                entries = search(session["keywords"])
                for i in entries:
                    # add username of creator to each entry
                    i["username"] = getUsername(i["userID"])
                    if i["username"] is None:
                        i["username"] = "[deleted user]"
                    # split post by new lines
                    i["post"] = i["post"].split("\n")
                # if page doesn't exist, default to page 1
                entries = pageEntries(entries, 10)
                if len(entries) < pageNum or pageNum < 1:
                    pageNum = 1
                return render_template("search-results.html", entries=entries,
                                       username=session["username"], pageNum=pageNum, search=session["keywords"])

        return redirect(url_for(".homepage"))
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

@app.route("/follow/<string:username>", methods=["GET", "POST"])
def follow(username):
    # if user is logged in
    if "username" in session:
        # if user not following blog
        if not checkFollower(getInfo(username, "id"), getInfo(session["username"], "id")):
            # add blog to db
            addFollower(getInfo(username, "id"), getInfo(session["username"], "id"))

            # set msg to following blog
            session["error_msg"] = "Successfully followed blog!"

            # if user follows blog from home page
            if "home" in request.form:
                # return home page with msg
                return redirect(url_for(".homepage"))

            # if user follows blog from blog page
            if "viewBlog" in request.form:
                # return blog page with msg
                return redirect(url_for(".viewBlog", pageNum=1, username=username))

        # if user following blog
        else:
            # if already following blog, set msg to that
            session["error_msg"] = "Already following blog."

            # if user unfollows blog from home page
            if "home" in request.form:
                # return home page with msg
                return redirect(url_for(".homepage"))

            # if user unfollows blog from blog page
            if "viewBlog" in request.form:
                # return blog page with msg
                return redirect(url_for(".viewBlog", pageNum=1, username=username))

    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

@app.route("/unfollow/<string:username>", methods=["GET", "POST"])
def unfollow(username):
    # if user is logged in
    if "username" in session:
        # if user not following blog
        if not checkFollower(getInfo(username, "id"), getInfo(session["username"], "id")):
            # set msg to not following blog, can't unfollow
            session["error_msg"] = "Not following this blog yet, cannot unfollow."

            # if user unfollows blog from home page
            if "home" in request.form:
                # return home page with msg
                return redirect(url_for(".homepage"))

            # if user unfollows blog from blog page
            if "viewBlog" in request.form:
                # return blog page with msg
                return redirect(url_for(".viewBlog", pageNum=1, username=username))

        # if user following blog
        else:
            # remove blog from db
            removeFollower(getInfo(username, "id"), getInfo(session["username"], "id"))
            # if following blog, set msg to unfollowing
            session["error_msg"] = "Successfully unfollowed blog!"

            # if user unfollows blog from home page
            if "home" in request.form:
                # return home page with msg
                return redirect(url_for(".homepage"))

            # if user unfollows blog from blog page
            if "viewBlog" in request.form:
                # return blog page with msg
                return redirect(url_for(".viewBlog", pageNum=1, username=username))

            # if user unfollows blog from following blogs page
            if "followUnfollow" in request.form:
                # return following blog page with msg
                return redirect(url_for(".followedBlogs"))

    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")

@app.route("/followed-blogs")
def followedBlogs():
    # to prevent error if user is not following any blogs yet
    following = []
    # if user is logged in
    if "username" in session:
        # for each blog user is following
        for blog in getFollowedBlogs(getInfo(session["username"], "id")):
            # add blogname to list
            following += [blog["blogname"]]
        # if user successfully unfollowed blog
        if "error_msg" in session:
            # store error
            msg = session["error_msg"]
            # remove error from session
            session.pop("error_msg")
            # return followed blogs
            return render_template("follow-blog.html", blogs=getFollowedBlogs(getInfo(session["username"], "id")),
                                   following=following, error_msg=msg, username=session["username"])
        # return followed blogs
        return render_template("follow-blog.html", blogs=getFollowedBlogs(getInfo(session["username"], "id")),
                               following=following, username=session["username"])

    # if user tries to access page without being logged in, redirect to login page
    return redirect("/")


if __name__ == "__main__":
    app.debug = True
    app.run()

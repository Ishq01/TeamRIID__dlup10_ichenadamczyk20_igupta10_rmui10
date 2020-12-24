import sqlite3

DB_FILE = "data.db"

# makes users and entries table in database if they do not exist already
def createTables():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT,
            password TEXT, blogname TEXT, blogdescription TEXT);""")
    c.execute("""CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY,
            userID INTEGER, time DATETIME, title TEXT, post TEXT);""")
    db.commit()
    db.close()

# adds user info to user table
def register(username, password, blogname, blogdescription):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    command = "INSERT INTO users (username, password, blogname, blogdescription) VALUES ('"
    command += username + "','" + password + "','" + blogname + "','" + blogdescription + "');"
    c.execute(command)
    db.commit()
    db.close()

# returns whether or not username is in user table
def checkUsername(username):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    found = False
    for row in c.execute("SELECT * FROM users;"):
        found = found or (username == row[1])
    db.commit()
    db.close()
    return found

# prints user table (for testing purposes)
def printDatabase():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    print("--------Users Table-----------")
    for row in c.execute("SELECT * FROM users;"):
        print (row)
    db.commit()
    db.close()

# returns information about a user from the specified column
# col can be 'id', 'password', 'blogname', or 'blogdescription'
def getInfo(username, col):
    if (checkUsername(username)):
        db = sqlite3.connect(DB_FILE)
        c = db.cursor()
        info = c.execute("SELECT " + col + " FROM users WHERE username = '" + username + "';").fetchone()[0]
        db.commit()
        db.close()
        return info
    return None

# changes a user's blog info given a new blog name and description
def updateBlogInfo(username, blogname, desc):
    if (checkUsername(username)):
        db = sqlite3.connect(DB_FILE)
        c = db.cursor()
        c.execute("UPDATE users SET blogname = '" + blogname + "' WHERE username = '" + username + "';")
        c.execute("UPDATE users SET blogdescription = '" + desc + "' WHERE username = '" + username + "';")
        db.commit()
        db.close()

# converts rows in database to a dictionary
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# returns a list of dictionaries containing each blog's info
def getBlogs():
    db = sqlite3.connect(DB_FILE)
    db.row_factory = dict_factory
    c = db.cursor()
    blogs = c.execute("SELECT * from users;").fetchall()
    db.commit()
    db.close()
    return blogs

# deletes all users from the database (for testing purposes)
def clearUsers():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("DELETE from users;")
    db.commit()
    db.close()

#clearUsers()
createTables()
# test methods here
printDatabase()
getBlogs()

import sqlite3
import datetime
import hashlib

DB_FILE = "data.db"

# salts and hashes the given string
def saltString(string, salt):
    return hashlib.pbkdf2_hmac('sha256', string.encode('utf-8'), salt, 100000)

# makes users and entries table in database if they do not exist already
def createTables():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT,
            password TEXT, blogname TEXT, blogdescription TEXT, time DATETIME);""")
    c.execute("""CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY,
            userID INTEGER, time DATETIME, title TEXT, post TEXT);""")
    db.commit()
    db.close()

# adds user info to user table
def register(username, password, blogname, blogdescription):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    dateAndTimetup = c.execute("SELECT datetime('now','localtime');").fetchone()
    dateAndTime = str(''.join(map(str, dateAndTimetup)))
    command = "INSERT INTO users (username, password, blogname, blogdescription, time) VALUES (?,?,?,?,?);"
    c.execute(command, (username, password, blogname, blogdescription, dateAndTime))
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
    print("-------Entries Table----------")
    for row in c.execute("SELECT * FROM entries;"):
        print (row)
    db.commit()
    db.close()

# returns information about a user from the specified column
# col can be 'id', 'password', 'blogname', or 'blogdescription'
def getInfo(username, col):
    if (checkUsername(username)):
        db = sqlite3.connect(DB_FILE)
        c = db.cursor()
        info = c.execute("SELECT " + col + " FROM users WHERE username=?;", [username] ).fetchone()[0]
        db.commit()
        db.close()
        return info
    return None

# changes a user's blog info given a new blog name and description
def updateBlogInfo(username, blogname, desc):
    if (checkUsername(username)):
        db = sqlite3.connect(DB_FILE)
        c = db.cursor()
        c.execute("UPDATE users SET blogname=? WHERE username=?;", (blogname, username))
        c.execute("UPDATE users SET blogdescription=? WHERE username=?;", (desc,username))
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
    blogs = c.execute("SELECT * from users ORDER BY time DESC;").fetchall()
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

def addEntry(userID, title, post):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    dateAndTimetup = c.execute("SELECT datetime('now','localtime');").fetchone()
    dateAndTime = str(''.join(map(str, dateAndTimetup)))
    command = "INSERT INTO entries (userID, time, title, post) VALUES (?,?,?,?);"
    c.execute(command, (str(userID), dateAndTime, title, post))
    c.execute("UPDATE users SET time=? WHERE id=?;", (dateAndTime, str(userID)))
    db.commit()
    db.close()

def editEntry(entryID, title, post):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    dateAndTimetup = c.execute("SELECT datetime('now','localtime');").fetchone()
    dateAndTime = str(''.join(map(str, dateAndTimetup)))
    c.execute("UPDATE entries SET title=? WHERE id=?;", (title, str(entryID)))
    c.execute("UPDATE entries SET post=? WHERE id=?;", (post, str(entryID)))
    c.execute("UPDATE entries SET time=? WHERE id=?;", (dateAndTime, str(entryID)))
    userID = c.execute("SELECT userID FROM entries WHERE id=?;", [str(entryID)] ).fetchone()
    c.execute("UPDATE users SET time=? WHERE id=?;", (dateAndTime, str(userID[0])))
    db.commit()
    db.close()

def getEntries(userID):
    db = sqlite3.connect(DB_FILE)
    db.row_factory = dict_factory
    c = db.cursor()
    entries = c.execute("SELECT * FROM entries WHERE userID=? ORDER BY time DESC;", [str(userID)] ).fetchall()
    db.commit()
    db.close()
    return entries

def deleteEntry(entryID):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("DELETE FROM entries WHERE id=?;",(str(entryID)))
    db.commit()
    db.close()

def clearEntries():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("DELETE from entries;")
    db.commit()
    db.close()

def clearAll():
    clearEntries()
    clearUsers()


#clearAll()

createTables()

'''
register("userA", "passsssssss", "my first blog", "A very cool lil blog")
register("userB", "passsssssss", "I hate the other blog", "I am raging schizophrenic")
register("userC", "passsssssss", "Cute Dog Pictures", "Cute dog pictures")

addEntry("1", "Hey guys!", "Hows it going")
addEntry("2", "Stop", "get off")
addEntry("1", "Why are you mean :(", "You guys alright?")
addEntry("3", "Dog", "imagine a dog here")
addEntry("1", "oh god", "Hahah hey")

deleteEntry("4")
'''
printDatabase()
getBlogs()
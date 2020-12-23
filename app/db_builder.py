import sqlite3

DB_FILE = "data.db"

def createTables():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT,
            password TEXT, blogname TEXT, blogdescription TEXT);""")
    c.execute("""CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY,
            userID INTEGER, time DATETIME, title TEXT, post TEXT);""")
    db.commit()
    db.close()


def register(username, password, blogname, blogdescription):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    command = "INSERT INTO users (username, password, blogname, blogdescription) VALUES ('"
    command += username + "','" + password + "','" + blogname + "','" + blogdescription + "');"
    c.execute(command)
    db.commit()
    db.close()

def checkUsername(username):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    for row in c.execute("SELECT * FROM users;"):
        if (username == row[1]):
            return True
    return False
    db.commit()
    db.close()

def printDatabase():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    print("--------Users Table-----------")
    for row in c.execute("SELECT * FROM users;"):
        print (row)
    db.commit()
    db.close()

def getPassword(username):
    if (checkUsername(username)):
        db = sqlite3.connect(DB_FILE)
        c = db.cursor()
        password = c.execute("SELECT password FROM users WHERE username = '" + username + "';").fetchone()[0]
        db.commit()
        db.close()
        return password
    return None

def clearUsers():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("DELETE from users");
    db.commit()
    db.close()

createTables()
# test methods here
printDatabase()

import sqlite3

DB_FILE = "data.db"
db = sqlite3.connect(DB_FILE)
c = db.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT,
            password TEXT, blogname TEXT, blogdescription TEXT);""")
c.execute("""CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY,
            userID INTEGER, time DATETIME, title TEXT, post TEXT);""")

def register(username, password, blogname, blogdescription):
    command = "INSERT INTO users (username, password, blogname, blogdescription) VALUES ('"
    command += username + "','" + password + "','" + blogname + "','" + blogdescription + "');"
    c.execute(command)

def checkUsername(username):
    for row in c.execute("SELECT * FROM users;"):
        if (username == row[1]):
            return True
    return False

def printDatabase():
    print("--------Users Table-----------")
    for row in c.execute("SELECT * FROM users;"):
        print (row)

register("user1", "pass", "blog", "description")
print("Should print true: " + str(checkUsername("user1")))
print("Should print false: " + str(checkUsername("user2")))
register("user2", "pass1", "blog1", "description1")
printDatabase()



#db.commit()
db.close()

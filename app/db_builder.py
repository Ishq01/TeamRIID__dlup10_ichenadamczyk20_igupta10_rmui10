import sqlite3

DB_FILE = "data.db"
db = sqlite3.connect(DB_FILE)
c = db.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT,
            password TEXT, blogname TEXT, blogdescription TEXT);""")
c.execute("""CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY,
            userID INTEGER, time DATETIME, title TEXT, post TEXT);""")

def register(username, password, blogname, blogdescription):
    command = "INSERT INTO users (username, password, blogname, blogdescription) VALUES ('" + username + "','" + password + "','" + blogname + "','" + blogdescription + "');"
    c.execute(command)

register("user2", "pass", "blog", "description")
register("user1", "pass1", "blog1", "description1")
for row in c.execute("SELECT * FROM users;"):
    print(row[1])

db.close()

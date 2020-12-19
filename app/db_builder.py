import sqlite3

DB_FILE = "data.db"
db = sqlite3.connect(DB_FILE)
c = db.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER primary key, username TEXT, password TEXT, blogname TEXT, blogdescription TEXT);")
c.execute("CREATE TABLE IF NOT EXISTS entries (id INTEGER primary key, userID INTEGER, time DATETIME, title TEXT, post TEXT);")

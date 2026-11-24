
import os
import turso_serverless


def get_db():
    cur.execute("CREATE TABLE IF NOT EXISTS tickets(ID INTEGER PRIMARY KEY AUTOINCREMENT, code INTEGER, username TEXT, receiver TEXT, title TEXT, message TEXT, file BLOB, date TEXT, time TEXT, info TEXT, status TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS all_users(ID INTEGER PRIMARY KEY AUTOINCREMENT, namefamily TEXT, username TEXT UNIQUE, password TEXT, status TEXT, access TEXT, token TEXT, tel TEXT, email TEXT, role TEXT)")
    
    return turso_serverless.connect(
        os.environ["TURSO_DATABASE_URL"],
        auth_token=os.environ["TURSO_AUTH_TOKEN"]
    )

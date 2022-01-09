import sqlite3

con = sqlite3.connect('database\database_administrator.db')
my_cursor = con.cursor()

def getAll():
    my_cursor.execute("SELECT * FROM administrator")
    result = my_cursor.fetchall()
    return result

def apply_Changes(username, password):
    my_cursor.execute(f"UPDATE administrator SET username = '{username}', password = '{password}'")
    con.commit()
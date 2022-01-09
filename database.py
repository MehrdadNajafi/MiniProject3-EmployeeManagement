import sqlite3

con = sqlite3.connect('database\database.db')
my_cursor = con.cursor()

def getAll():
    my_cursor.execute("SELECT * FROM Employee")
    result = my_cursor.fetchall()
    return result

def add_Employee(id, name, family, nc, birthday):
    my_cursor.execute(f"INSERT INTO Employee (id, name, family, national_code, birthday) VALUES ({id}, '{name}', '{family}', {nc}, '{birthday}')")
    con.commit()

def delete_Employee(id):
    my_cursor.execute(f"DELETE FROM Employee WHERE id = {id}")
    con.commit()
    
def edit_Employee(id, name, family, nc, birthday):
    my_cursor.execute(f"UPDATE Employee SET name = '{name}', family = '{family}', national_code = {nc}, birthday = '{birthday}' WHERE id = {id}")
    con.commit()
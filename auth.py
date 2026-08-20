import sqlite3
def dbconn (): 
    conn=sqlite3.connect("data_labeling.db")
    return conn


def user_exist(email):
    conn=dbconn()
    cur=conn.cursor()
    sorgu="SELECT *FROM users Where email= ?"
    cur.execute(sorgu,(email,))

    user =cur.fetchone()
    conn.close() 
    if user is not None :
        return True
    else: 
        return False


def register(email,password_hash):
    if user_exist(email):
        return False 
    conn=dbconn()
    cur=conn.cursor()
    sorgu="INSERT INTO users (email, password_hash) VALUES (?, ?)"
    cur.execute(sorgu,(email,password_hash))
    conn.commit()
    conn.close()
    return True


def  login(email,password_hash ):
    conn=dbconn()
    cur=conn.cursor()
    sorgu="SELECT id FROM users where email= ? and password_hash = ? "
    cur.execute(sorgu,(email,password_hash))
    user =cur.fetchone()
    conn.close()
    if user is not None :
        return user[0]
    else:
        return None

    

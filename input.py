import sqlite3
import re
def dbconn ():
    conn=sqlite3.connect("data_labeling.db")
    return conn


def parse_text_input(raw_text:str):
    if not raw_text:
        return[]

    lines= re.split(r'[.!?\n]+', raw_text)

    clean_sentences=[]


    for line in lines:
        clean_line=line.strip()
        if clean_line:
            clean_sentences.append(clean_line)



    return clean_sentences

def create_project(user_id : int ,title : str , description:str,task_type:str):
    conn=dbconn()
    cur=conn.cursor()
    sorgu="INSERT INTO projects(user_id,title ,description,task_type) VALUES (?,?,?,?) RETURNING id"
    cur.execute(sorgu ,(user_id,title,description,task_type))
    project_id=cur.fetchone()[0]
    conn.commit()
    conn.close()
    return project_id


def project_adder_text(project_id :int,user_id:int ,clean_sentences:list ):

    conn=dbconn()
    cur=conn.cursor()

    task_data=[]
    for sentence in clean_sentences:
        paket=(project_id,user_id,sentence)
        task_data.append(paket)

    sorgu="INSERT INTO tasks(project_id,assigned_user_id,data_content) VALUES (?,?,?)"
    cur.executemany(sorgu, task_data)
    conn.commit()
    conn.close()


def get_project (user_id : int ):
    conn=dbconn()
    cur=conn.cursor()
    sorgu="SELECT * FROM  projects WHERE user_id = ?"
    cur.execute(sorgu ,(user_id,))
    projects=cur.fetchall()
    conn.close()
    return projects

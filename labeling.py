import sqlite3


def dbconn():
    conn=sqlite3.connect("data_labeling.db")
    return conn



def data_comiter(project_id: int, data_content: str,assigned_user_id:int):
    conn=dbconn()
    curr=conn.cursor()
    sorgu="Insert into tasks (project_id,data_content,assigned_user_id) VALUES (?,?,?)"
    curr.execute(sorgu ,(project_id,data_content,assigned_user_id))
    task_id =curr.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_next_task(assigned_user_id ,project_id):
    conn=dbconn()
    cur=conn.cursor()
    sorgu="SELECT id,data_content From tasks  WHERE  assigned_user_id=? AND project_id =?and status='PENDING' LIMIT 1 "
    cur.execute(sorgu,(assigned_user_id,project_id))
    task =cur.fetchone()
    conn.close()
    return task

def labeler(id : int ,label_id : int ,user_id:int):
    conn=dbconn()
    cur=conn.cursor()
    sorgu_ins="INSERT INTO annotations(task_id,label_id,user_id) VALUES (?,?,?)"
    cur.execute(sorgu_ins ,(id,label_id,user_id))
    sorgu_update="  UPDATE tasks SET status = 'COMPLETED' WHERE id = ?"
    cur.execute(sorgu_update,((id,)))
    conn.commit()
    conn.close()

def completed_task(project_id :int ):
    conn=dbconn()
    cur=conn.cursor()
    sorgu = "SELECT tasks.data_content, annotations.label_id FROM annotations JOIN tasks ON annotations.task_id = tasks.id WHERE tasks.project_id = ?"
    cur.execute(sorgu,(project_id,))
    results =cur.fetchall()
    conn.close()
    return results


def get_remaining_count(project_id):
    conn = dbconn()
    cur = conn.cursor()

    sorgu = "SELECT COUNT(*) FROM tasks WHERE project_id = ? AND status = 'PENDING'"

    cur.execute(sorgu, (project_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count


def export_ended_task(project_id : int):
    conn=dbconn()
    cur=conn.cursor()
    sorgu="SELECT tasks.data_content, labels.name, labels.color_code FROM tasks JOIN annotations ON tasks.id = annotations.task_id JOIN labels ON annotations.label_id = labels.id WHERE tasks.project_id = ?"
    cur.execute(sorgu,(project_id,))
    finished_taks=cur.fetchall()
    conn.close()
    return finished_taks
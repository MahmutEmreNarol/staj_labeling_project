import sqlite3


def dbconn():
    conn=sqlite3.connect("data_labeling.db")
    return conn



def data_comiter(project_id: int, data_content: str,assigned_user_id:int):
    conn=dbconn()
    curr=conn.cursor()
    sorgu= 'Insert into tasks (project_id,data_content,assigned_user_id) VALUES (?,?,?)'
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
    sorgu ='SELECT tasks.id, tasks.data_content, labels.name, labels.color_code FROM annotations  JOIN tasks ON annotations.task_id = tasks.id   JOIN labels ON annotations.label_id = labels.id  WHERE tasks.project_id = ?'
    cur.execute(sorgu,(project_id,))
    results =cur.fetchall()
    conn.close()
    return results

def completed_ner_task(project_id: int):
    conn = dbconn()
    cur = conn.cursor()
    sorgu ='SELECT tasks.id, entity_annotations.selected_text, labels.name, labels.color_code FROM entity_annotations JOIN annotations ON entity_annotations.annotation_id = annotations.id JOIN tasks ON annotations.task_id = tasks.id JOIN labels ON entity_annotations.label_id = labels.id WHERE tasks.project_id = ?'
    cur.execute(sorgu, (project_id,))
    results = cur.fetchall()
    conn.close()
    return results


def complete_task(task_id: int):
    conn = dbconn()
    cur = conn.cursor()
    sorgu = "UPDATE tasks SET status = 'COMPLETED' WHERE id = ?"
    cur.execute(sorgu, (task_id,))
    conn.commit()
    conn.close()

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


def export_ended_ner_task(project_id: int):
    conn = dbconn()
    cur = conn.cursor()
    sorgu = """
        SELECT tasks.data_content, entity_annotations.selected_text, labels.name, 
               entity_annotations.start_offset, entity_annotations.end_offset
        FROM tasks
        JOIN annotations ON tasks.id = annotations.task_id
        JOIN entity_annotations ON annotations.id = entity_annotations.annotation_id
        JOIN labels ON entity_annotations.label_id = labels.id
        WHERE tasks.project_id = ?
    """
    cur.execute(sorgu, (project_id,))
    results = cur.fetchall()
    conn.close()
    return results


def export_ended_object_task(project_id: int):
    conn = dbconn()
    cur = conn.cursor()
    sorgu = """
        SELECT tasks.data_content, labels.name, bounding_boxes.x, bounding_boxes.y, 
               bounding_boxes.width, bounding_boxes.height
        FROM tasks
        JOIN bounding_boxes ON tasks.id = bounding_boxes.task_id
        JOIN labels ON bounding_boxes.label_id = labels.id
        WHERE tasks.project_id = ?
    """
    cur.execute(sorgu, (project_id,))
    results = cur.fetchall()
    conn.close()
    return results


def update_annotation(task_id: int, label_id: int, user_id: int):
    conn = dbconn()
    cur = conn.cursor()

    sorgu = "UPDATE annotations SET label_id = ? WHERE task_id = ? AND user_id = ?"
    cur.execute(sorgu, (label_id, task_id, user_id))

    conn.commit()
    conn.close()



def ner_labeler(task_id:int ,label_id : int ,user_id ,start_offset,  end_offset, selected_text ):
    conn=dbconn()
    cur=conn.cursor()
    sorgu1='INSERT INTO annotations(task_id,label_id,user_id) VALUES (?,?,?)'
    cur.execute(sorgu1,(task_id,label_id,user_id))
    annotation_id = cur.lastrowid
    sorgu2 = "INSERT INTO entity_annotations (annotation_id, label_id, start_offset, end_offset, selected_text) VALUES (?, ?, ?, ?, ?)"
    cur.execute(sorgu2,(annotation_id ,label_id,start_offset,  end_offset, selected_text))
    conn.commit()
    conn.close()


def object_detect(task_id: int, label_id: int, user_id: int, x: float, y: float, width: float, height: float):
    conn = dbconn()
    cur = conn.cursor()

    sorgu1 = "INSERT INTO annotations(task_id, label_id, user_id) VALUES (?, ?, ?)"
    cur.execute(sorgu1, (task_id, label_id, user_id))

    annotation_id = cur.lastrowid

    sorgu2 = "INSERT INTO bounding_boxes(annotation_id, task_id, label_id, x, y, width, height) VALUES (?, ?, ?, ?, ?, ?, ?)"
    cur.execute(sorgu2, (annotation_id, task_id, label_id, x, y, width, height))

    conn.commit()
    conn.close()


def get_task_by_id_and_project(task_id: int, project_id: int):
    conn = dbconn()
    cur = conn.cursor()
    sorgu = "SELECT id, data_content FROM tasks WHERE id = ? AND project_id = ?"
    cur.execute(sorgu, (task_id, project_id))
    task = cur.fetchone()
    conn.close()
    return task


def get_prev_task_id(project_id: int, current_task_id: int):
    conn = dbconn()
    cur = conn.cursor()
    sorgu = "SELECT id FROM tasks WHERE project_id = ? AND id < ? ORDER BY id DESC LIMIT 1"
    cur.execute(sorgu, (project_id, current_task_id))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

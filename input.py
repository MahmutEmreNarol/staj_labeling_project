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

def parse_word_input(raw_text: str):
    if not raw_text:
        return []
    words = raw_text.split()
    clean_words = [w.strip() for w in words if w.strip()]
    return clean_words

LABEL_COLORS = [
    "#007bff",  # 1. Mavi
    "#ffc107",  # 2. Sarı
    "#28a745",  # 3. Yeşil
    "#dc3545",  # 4. Kırmızı
    "#6f42c1",  # 5. Mor
    "#fd7e14",  # 6. Turuncu
    "#17a2b8",  # 7. Turkuaz
    "#e83e8c",  # 8. Pembe
]

def create_project(user_id: int, title: str, description, task_type, labels: list):
    conn = dbconn()
    cur = conn.cursor()

    sorgu = "INSERT INTO projects(user_id,title,description,task_type) VALUES (?,?,?,?) RETURNING id"
    cur.execute(sorgu, (user_id, title, description, task_type))

    project_id = cur.fetchone()[0]

    label_data = []
    for idx, item in enumerate(labels):
        if isinstance(item, (list, tuple)):
            name, color = item[0], item[1]
        else:
            name, color = item, LABEL_COLORS[idx % len(LABEL_COLORS)]
        label_data.append((project_id, name, color))

    cur.executemany(
        "INSERT INTO labels(project_id, name, color_code) VALUES (?, ?, ?)",
        label_data
    )

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


def get_project (user_id : int ,task_tpye : str ):
    conn=dbconn()
    cur=conn.cursor()
    sorgu="SELECT * FROM  projects WHERE user_id = ? AND task_type =?"
    cur.execute(sorgu ,(user_id, task_tpye))
    projects=cur.fetchall()
    conn.close()
    return projects

def get_allprojects(user_id: int):
    conn=dbconn()
    cur=conn.cursor()
    sorgu="Select *From projects WHERE user_id= ?"
    cur.execute(sorgu,(user_id,))
    all_projects=cur.fetchall()

    conn.close()
    return all_projects


def calculate_progress(project_id:int):
    conn=dbconn()
    cur=conn.cursor()
    sorgu1 = "SELECT COUNT(*) FROM tasks WHERE project_id = ? AND status = 'PENDING'"
    sorgu2 = "SELECT COUNT(*) FROM tasks WHERE project_id = ? AND status = 'COMPLETED'"
    cur.execute(sorgu1,(project_id,))
    count_pending=cur.fetchone()[0]
    cur.execute(sorgu2, (project_id,))
    count_completed=cur.fetchone()[0]
    calculation=100

    if count_pending > 0 :
        calculation=(count_completed/ (count_pending+count_completed))*100


    conn.close()
    return  count_completed,count_pending, calculation

def get_labels(project_id: int):
    conn = dbconn()
    cur = conn.cursor()
    sorgu = "SELECT id, name, color_code FROM labels WHERE project_id = ?"
    cur.execute(sorgu, (project_id,))
    labels = cur.fetchall()
    conn.close()
    return labels


def get_current_boxes(task_id: int):
    conn = dbconn()
    cur = conn.cursor()
    sorgu = 'SELECT bounding_boxes.id, bounding_boxes.label_id, labels.name, labels.color_code, bounding_boxes.x, bounding_boxes.y, bounding_boxes.width, bounding_boxes.height FROM bounding_boxes JOIN labels ON bounding_boxes.label_id = labels.id WHERE bounding_boxes.task_id = ?'
    cur.execute(sorgu, (task_id,))
    boxes = cur.fetchall()
    conn.close()
    return boxes

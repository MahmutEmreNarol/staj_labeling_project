import csv
import io
import os
import shutil
import uuid
from typing import List
from fastapi import FastAPI, Request, Form, UploadFile, File, status, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from auth import login as db_login
from auth import register as db_register
from fastapi.responses import RedirectResponse
from labeling import get_next_task, labeler,get_remaining_count,completed_task,export_ended_task,update_annotation,ner_labeler,completed_ner_task ,complete_task,object_detect, get_task_by_id_and_project, get_prev_task_id, export_ended_ner_task, export_ended_object_task, dbconn
from input import parse_text_input, parse_word_input, create_project, project_adder_text, get_project, get_allprojects,calculate_progress,get_labels,get_current_boxes

app=FastAPI()
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates=Jinja2Templates(directory="Templates")

@app.get("/")
def home (request:Request):
    return templates.TemplateResponse(request=request, name="home.html")
##Burda yapıyoruz o  ana menü kısmını


@app.get("/havadurum")
def hava(request :Request):
    return templates.TemplateResponse( request=request,name="index.html")


@app.post("/login")
def login_post(email: str =Form(...),password : str =Form()):
    user_id=db_login(email,password)

    if user_id is not None:
       response = RedirectResponse(url="/dashboard",status_code=status.HTTP_303_SEE_OTHER)
       response.set_cookie(key="user_id",value=str(user_id))
       return response
    else :
        return{"Giriş başarısız mail veya password hatalı"}


@app.get("/login")
def login_get(request:Request):
    return templates.TemplateResponse(request=request ,name="login.html")


@app.get("/logout")
def logout():

    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


    response.delete_cookie(key="user_id")

    return response

@app.get("/register")
def register_get(request :Request):
    return  templates.TemplateResponse(request=request,name="register.html")
@app.post("/register")
def  register_post(email:str=Form(),password:str =Form()):
    if db_register(email,password):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    else :
        return {"Kullanıcı zaten kayıtlı "}

@app.get("/dashboard")
def dashboard_get(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(request=request, name="dashboard.html")
@app.get("/sentence")
def sentence_get(request :Request ,project_id:int =None):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


    task = None
    show_task = []
    show_task_count = 0
    task_id = None
    content = ""
    labels=[]
    if project_id:

        task=get_next_task(int(user_id),project_id=project_id)
        show_task = completed_task(int(project_id))
        show_task_count = get_remaining_count(int(project_id))
        labels=get_labels(project_id)
        if task:
            task_id=task[0]
            content=task[1]
        else:
            task_id=None
            content="Tebrikler Başka cümle kalmadı"

    projects = get_project(int(user_id), "Text")

    return templates.TemplateResponse(request=request,name="sentence.html",context={
                                          "task_id": task_id,
                                          "task_content":content,
                                          "projects":projects,
                                          "selected_project_id": project_id ,
                                          "remaining_count": show_task_count,
                                          "completed_tasks": show_task,
                                          "labels":labels
    })
@app.post("/sentence")
def sentence_post(request :Request,task_id:int =Form(...),label_id=Form(...),project_id:int =Form(...)):
    user_id=request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    labeler(task_id,label_id,int(user_id))
    ##parse_text_input(raw_text=raw_text)
    return RedirectResponse(url=f"/sentence?project_id={project_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/word")
def word_get(request: Request, project_id: int = None):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    task = None
    show_task = []
    show_task_count = 0
    task_id = None
    content = ""
    labels=[]
    if project_id:
        task = get_next_task(int(user_id), project_id=project_id)
        show_task = completed_task(int(project_id))
        show_task_count = get_remaining_count(int(project_id))
        labels = get_labels(project_id)
        if task:
            task_id = task[0]
            content = task[1]
        else:
            task_id = None
            content = "Tebrikler Başka kelime kalmadı"

    projects = get_project(int(user_id), "Word")

    return templates.TemplateResponse(request=request, name="word.html", context={
        "task_id": task_id,
        "task_content": content,
        "projects": projects,
        "selected_project_id": project_id,
        "remaining_count": show_task_count,
        "completed_tasks": show_task,
        "labels": labels
    })

@app.post("/word")
def word_post(request: Request, task_id: int = Form(...), label_id=Form(...), project_id: int = Form(...)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    labeler(task_id, label_id, int(user_id))
    return RedirectResponse(url=f"/word?project_id={project_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/create-project-word")
async def create_project_word_post(
    request: Request,
    project_name: str = Form(...),
    raw_text: str = Form(...),
    label_names: List[str] = Form([]),
    label_colors: List[str] = Form([])
):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    clean_words = parse_word_input(raw_text)
    label_list = [
        (name.strip(), color)
        for name, color in zip(label_names, label_colors)
        if name.strip()
    ]

    project_id = create_project(int(user_id), project_name, raw_text, "Word", label_list)
    project_adder_text(project_id, int(user_id), clean_words)

    return RedirectResponse(url=f"/word?project_id={project_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/create-project")
async def create_project_post(
    request: Request,
    project_name: str = Form(...),
    raw_text: str = Form(...),
    label_names: List[str] = Form([]),
    label_colors: List[str] = Form([])
):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    cleandata = parse_text_input(raw_text)
    label_list = [
        (name.strip(), color)
        for name, color in zip(label_names, label_colors)
        if name.strip()
    ]

    project_id = create_project(int(user_id), project_name, raw_text, "Text", label_list)
    project_adder_text(project_id, int(user_id), cleandata)

    return RedirectResponse(url=f"/sentence?project_id={project_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/image")
def image_get(request: Request, project_id: int = None):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    task = None
    show_task = []
    show_task_count = 0
    task_id = None
    content = ""
    labels = []

    if project_id:
        task = get_next_task(int(user_id), project_id=project_id)
        show_task = completed_task(int(project_id))
        show_task_count = get_remaining_count(int(project_id))
        labels = get_labels(project_id)

        if task:
            task_id = task[0]
            content = task[1]
        else:
            task_id = None
            content = ""

    projects = get_project(int(user_id), "IMAGE")

    return templates.TemplateResponse(
        request=request,
        name="image.html",
        context={
            "task_id": task_id,
            "task_content": content,
            "projects": projects,
            "selected_project_id": project_id,
            "remaining_count": show_task_count,
            "completed_tasks": show_task,
            "labels": labels
        }
    )

@app.post("/image")
def image_post(request: Request, task_id: int = Form(...), label_id=Form(...), project_id: int = Form(...)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    labeler(task_id, label_id, int(user_id))
    return RedirectResponse(url=f"/image?project_id={project_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/create-project-image")
async def create_project_image_post(
    request: Request,
    project_name: str = Form(...),
    files: List[UploadFile] = File(...),
    label_names: List[str] = Form([]),
    label_colors: List[str] = Form([])
):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    label_list = [
        (name.strip(), color)
        for name, color in zip(label_names, label_colors)
        if name.strip()
    ]

    project_id = create_project(
        int(user_id),
        project_name,
        f"{len(files)} görsel yüklendi",
        "IMAGE",
        label_list
    )

    image_paths = []
    upload_dir = os.path.join("static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    for file in files:
        if file.filename:
            file_ext = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
            file_path = os.path.join(upload_dir, unique_filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            relative_url = f"/static/uploads/{unique_filename}"
            image_paths.append(relative_url)

    project_adder_text(project_id, int(user_id), image_paths)

    return RedirectResponse(
        url=f"/image?project_id={project_id}",
        status_code=status.HTTP_303_SEE_OTHER
    )



@app.get("/export/{project_id}")
def export_get_csv(request: Request, project_id: int):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    conn = dbconn()
    cur = conn.cursor()
    cur.execute("SELECT task_type FROM projects WHERE id = ?", (project_id,))
    row = cur.fetchone()
    conn.close()
    task_type = row[0] if row else "Text"

    output = io.StringIO()
    writer = csv.writer(output)

    if task_type == "NER":
        writer.writerow(["Cümle Metni", "Varlık (Entity)", "Etiket", "Başlangıç İndeksi", "Bitiş İndeksi"])
        for r in export_ended_ner_task(project_id):
            writer.writerow(r)
    elif task_type == "OBJECT":
        writer.writerow(["Görsel Yolu", "Etiket", "X (%)", "Y (%)", "Genişlik (%)", "Yükseklik (%)"])
        for r in export_ended_object_task(project_id):
            writer.writerow(r)
    else:
        writer.writerow(["İçerik", "Etiket Adı", "Renk Kodu"])
        for r in export_ended_task(project_id):
            writer.writerow(r)

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=project_{project_id}_export.csv"
    return response




@app.post("/update-annotation")
def update_annotation_post(request: Request, task_id: int = Form(...), label_id=Form(...), project_id: int = Form(...),page_type:str=Form(...)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


    update_annotation(task_id, label_id, int(user_id))

    return RedirectResponse(url=f"/{page_type}?project_id={project_id}", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/projects")
def projects_get(request:Request,):
    user_id=request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login",status_code=status.HTTP_303_SEE_OTHER)
    all_projects=get_allprojects(user_id)



    return templates.TemplateResponse(request=request, name="projects.html", context={
        "projects":all_projects,
        "calculate_progress":calculate_progress

    })


@app.get("/NER")
def NER_get(request :Request ,project_id:int =None):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


    task = None
    show_task = []
    show_task_count = 0
    task_id = None
    content = ""
    labels = []

    if project_id:
        labels=get_labels(project_id)
        task = get_next_task(int(user_id),project_id=project_id)
        show_task = completed_ner_task(int(project_id))
        show_task_count = get_remaining_count(int(project_id))
        labels = get_labels(project_id)
        if task:
            task_id=task[0]
            content=task[1]
        else:
            task_id=None
            content="Tebrikler Başka cümle kalmadı"

    projects = get_project(int(user_id), "NER")

    return templates.TemplateResponse(request=request,name="NER.html",context={
                                          "task_id": task_id,
                                          "task_content":content,
                                          "projects":projects,
                                          "selected_project_id": project_id ,
                                          "remaining_count": show_task_count,
                                          "completed_tasks": show_task,
                                          "labels":labels
    })

@app.post("/create-project-NER")
async def create_project_NER_post(
    request: Request,
    project_name: str = Form(...),
    raw_text: str = Form(...),
    label_names: List[str] = Form([]),
    label_colors: List[str] = Form([])
):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    cleandata = parse_text_input(raw_text)
    label_list = [
        (name.strip(), color)
        for name, color in zip(label_names, label_colors)
        if name.strip()
    ]

    project_id = create_project(int(user_id), project_name, raw_text, "NER", label_list)
    project_adder_text(project_id, int(user_id), cleandata)

    return RedirectResponse(url=f"/NER?project_id={project_id}", status_code=status.HTTP_303_SEE_OTHER)





@app.get("/object")
def object_get(request: Request, project_id: int = None, task_id: int = None):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    active_task_id = None
    content = ""
    labels = []
    current_boxes = []
    remaining_count = 0
    completed_count = 0
    prev_task_id = None

    if project_id:
        labels = get_labels(project_id)
        remaining_count = get_remaining_count(project_id)
        completed_count = calculate_progress(project_id)[0]

        task = None
        if task_id:
            # Proje güvenliği: task_id seçili project_id'ye mi ait doğrula
            task = get_task_by_id_and_project(task_id, project_id)

        if not task:
            task = get_next_task(int(user_id), project_id)

        if task:
            active_task_id = task[0]
            content = task[1]
            current_boxes = get_current_boxes(active_task_id)
            prev_task_id = get_prev_task_id(project_id, active_task_id)

    projects = get_project(int(user_id), "OBJECT")

    return templates.TemplateResponse(request=request, name="object.html", context={
        "task_id": active_task_id,
        "task_content": content,
        "projects": projects,
        "selected_project_id": project_id,
        "remaining_count": remaining_count,
        "completed_count": completed_count,
        "prev_task_id": prev_task_id,
        "labels": labels,
        "current_boxes": current_boxes
    })

@app.post("/NER")
def NER_post(request :Request,task_id:int =Form(...),label_id=Form(...),project_id:int =Form(...),selected_text = Form(...) ,start_offset: int = Form(...) ,end_offset: int = Form(...)):
    user_id=request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    ner_labeler(task_id, label_id, int(user_id), start_offset, end_offset, selected_text)
    print(selected_text)

    return RedirectResponse(url=f"/NER?project_id={project_id}", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/NER/complete")
def NER_complete(request: Request, task_id: int = Form(...), project_id: int = Form(...)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    complete_task(task_id)

    return RedirectResponse(url=f"/NER?project_id={project_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/object")
def object_post(
    request: Request,
    task_id: int = Form(...),
    label_id: int = Form(...),
    project_id: int = Form(...),
    x: float = Form(...),
    y: float = Form(...),
    width: float = Form(...),
    height: float = Form(...)
):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    object_detect(
        task_id,
        label_id,
        int(user_id),
        x,
        y,
        width,
        height
    )

    return RedirectResponse(
        url=f"/object?project_id={project_id}&task_id={task_id}",
        status_code=status.HTTP_303_SEE_OTHER
    )


@app.post("/create-project-object")
async def create_project_object_post(
    request: Request,
    project_name: str = Form(...),
    files: List[UploadFile] = File(...),
    label_names: List[str] = Form([]),
    label_colors: List[str] = Form([])
):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    label_list = [
        (name.strip(), color)
        for name, color in zip(label_names, label_colors)
        if name.strip()
    ]

    project_id = create_project(int(user_id), project_name, f"{len(files)} görsel yüklendi", "OBJECT", label_list)

    image_paths = []
    upload_dir = os.path.join("static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    for file in files:
        if file.filename:
            file_ext = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
            file_path = os.path.join(upload_dir, unique_filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            relative_url = f"/static/uploads/{unique_filename}"
            image_paths.append(relative_url)

    project_adder_text(project_id, int(user_id), image_paths)

    return RedirectResponse(url=f"/object?project_id={project_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/object/complete")
def object_complete(request: Request, task_id: int = Form(...), project_id: int = Form(...)):
    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    complete_task(task_id)

    return RedirectResponse(url=f"/object?project_id={project_id}", status_code=status.HTTP_303_SEE_OTHER)
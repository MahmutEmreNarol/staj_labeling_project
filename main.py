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
from labeling import get_next_task, labeler,get_remaining_count,completed_task,export_ended_task
from input import parse_text_input, parse_word_input, create_project,project_adder_text,get_project



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
def dashboard_get(request:Request):
    return templates.TemplateResponse(request=request,name="dashboard.html")
@app.get("/sentence")
def sentence_get(request :Request ,project_id:int =None):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    task =None

    task = None
    show_task = []
    show_task_count = 0
    task_id = None
    content = ""
    if project_id:

        task=get_next_task(int(user_id),project_id=project_id)
        show_task = completed_task(int(project_id))
        show_task_count = get_remaining_count(int(project_id))
        if task:
            task_id=task[0]
            content=task[1]
        else:
            task_id=None
            content="Tebrikler Başka cümle kalmadı"

    projects=get_project(int(user_id))

    return templates.TemplateResponse(request=request,name="sentence.html",context={
                                          "task_id": task_id,
                                          "task_content":content,
                                          "projects":projects,
                                          "selected_project_id": project_id ,
                                          "remaining_count": show_task_count,
                                          "completed_tasks": show_task
    })
@app.post("/sentence")
def sentence_post(request :Request,task_id:int =Form(...),label_id=Form(...),project_id:int =Form(...)):
    user_id=request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    labeler(task_id,label_id,int(user_id))
    ##parse_text_input(raw_text=raw_text)
    return RedirectResponse(url=f"/sentence?project_id={project_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/create-project")
async def create_project_post(request :Request,project_name :str=Form(...) ,raw_text:str=Form()):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


    cleandata=parse_text_input(raw_text)
    project_id=create_project(int(user_id),project_name,raw_text,"Text")
    project_adder_text(project_id,int(user_id),cleandata)

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
    if project_id:
        task = get_next_task(int(user_id), project_id=project_id)
        show_task = completed_task(int(project_id))
        show_task_count = get_remaining_count(int(project_id))
        if task:
            task_id = task[0]
            content = task[1]
        else:
            task_id = None
            content = ""

    projects = get_project(int(user_id))

    return templates.TemplateResponse(request=request, name="image.html", context={
        "task_id": task_id,
        "task_content": content,
        "projects": projects,
        "selected_project_id": project_id,
        "remaining_count": show_task_count,
        "completed_tasks": show_task
    })

@app.post("/image")
def image_post(request: Request, task_id: int = Form(...), label_id=Form(...), project_id: int = Form(...)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    labeler(task_id, label_id, int(user_id))
    return RedirectResponse(url=f"/image?project_id={project_id}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/create-project-image")
async def create_project_image_post(request: Request, project_name: str = Form(...), files: List[UploadFile] = File(...)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    project_id = create_project(int(user_id), project_name, f"{len(files)} görsel yüklendi", "IMAGE")

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

    return RedirectResponse(url=f"/image?project_id={project_id}", status_code=status.HTTP_303_SEE_OTHER)



@app.get("/export/{project_id}")
def export_get_csv(request:Request, project_id:int):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    text_data=export_ended_task(project_id)
    output = io.StringIO()
    writer = csv.writer(output)

    # CSV Başlıkları
    writer.writerow(["Cümle Metni", "Etiket Adı", "Renk Kodu"])

    # Dönen veri listesini CSV'ye yazıyoruz
    for row in text_data:
        writer.writerow(row)
    response =Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=project_{project_id}_export.csv"
    return response
from fastapi import Depends, FastAPI, Request, Form, UploadFile, File, BackgroundTasks, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routes.database import get_db_sqlite_old, sessionLocal_pg, sessionLocal_sqlite,  Base_sqlite, Base_pg, engine_sqlite, Base_sqlite_old, engine_sqlite_old, engine_pg, get_db_pg, get_db_sqlite, get_db_sqlite_old, Base_sqlite_old
from routes.models import UserDetails, posts_old, posts
from routes.schema import UserLogin, Post
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
import shutil


#creating tables
Base_sqlite.metadata.create_all(bind=engine_sqlite)
Base_pg.metadata.create_all(bind=engine_pg)
Base_sqlite_old.metadata.create_all(bind=engine_sqlite_old)

app = FastAPI(title="FastAPI Challenge")


#Extra directory preparations
Base_dir = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=Base_dir / "static"), name="static")

templates = Jinja2Templates(directory=Base_dir / "templates")
Upload_dir = "static/Uploads"
os.makedirs(Upload_dir,exist_ok=True)

templates =  Jinja2Templates(directory=("templates"))




#           ---------------------------------------------ROUTERS--------------------------------------


#Reading the homepage
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("fastapi_practice.html", {"request": request, "title": "FastAPI Challenge"})

#signupFOrm Data
@app.post("/signUp")
async def signUp():
    pass

#Login FOrm Data
@app.post("/login")
async def login():
    pass



#----------------------------DONE----------------------------
#Create Post (Form + File Upload + Background Task)
@app.post("/upload")
async def upload_file(db: Session = Depends(get_db_sqlite),  
                      title: str = Form(...), content: str = Form(...), 
                      image: UploadFile = File(...), author: str = Form(...)):

    file_location = os.path.join(Upload_dir, image.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(image.file, f)

    db_posts = posts(author = author, title = title, content = content, fileName = image.filename)
    db.add(db_posts)
    db.commit()
    db.refresh(db_posts)
    db.close()
    return {"stored in" : file_location}


#----------------------------DONE----------------------------
#View Posts (Pagination + Filtering + Sorting)      
@app.get("/posts")
async def read_post(db: Session = Depends(get_db_sqlite_old), sort: str = Query("id"),
                    page: int = Query(1, ge=1, le=30), order: str = Query("asc"),
                    limit: int = Query(3, le=10), search: str = Query(None), 
                    ):
    
    query = db.query(posts_old)

    #search/filtering
    if search:
        query = query.filter(posts_old.title.ilike(f"%{search}%"))

    skip = (page -1 ) * limit

    post_count = query.count()

    #Order and sorting
    if order == "asc":
        query = query.order_by(getattr(posts_old, sort).asc())
    else:
        query = query.order_by(getattr(posts_old, sort).desc())

    #pagination
    result = query.offset(skip).limit(limit).all()
    return result



#Download Uploaded Image
@app.get("/image/{image_id}")
async def download_image():
    pass
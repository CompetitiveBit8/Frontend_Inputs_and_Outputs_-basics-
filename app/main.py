from fastapi import Depends, FastAPI, Response, Request, Form, UploadFile, File, BackgroundTasks, Query, HTTPException, Cookie
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db.database import get_db_sqlite_old, sessionLocal_pg, sessionLocal_sqlite,  Base_sqlite, Base_pg, engine_sqlite, Base_sqlite_old, engine_sqlite_old, engine_pg, get_db_pg, get_db_sqlite, get_db_sqlite_old, Base_sqlite_old
from app.models.models import UserDetails, posts_old, posts
from app.schema.schema import UserLogin, PostSchema
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.utils.auth_utils import hash_password, verify_password, create_access_token, decode_access_token, create_refresh_token, decode_refresh_token, get_current_user
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

templates = Jinja2Templates(directory="app" / Base_dir / "templates")
Upload_dir = "static/Uploads"
os.makedirs(Upload_dir,exist_ok=True)





#           ---------------------------------------------ROUTERS--------------------------------------


#Reading the homepage
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("fastapi_practice.html", {"request": request, "title": "FastAPI Challenge"})

#signupFOrm Data
@app.post("/signup")
async def signup(username=Form(...), password=Form(...), db: Session = Depends(get_db_pg)):
    user = db.query(UserDetails).filter(UserDetails.username == username).first()
    if user:
        raise HTTPException(status_code=401, detail="User already exists")

    hashed_password = hash_password(password)

    #schema
    new_user = UserLogin(
        username= username,
        password= hashed_password
    )
    #inputing to databse
    new_user = UserDetails(**new_user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"username": new_user.username, "password": new_user.password}

#Login FOrm Data
@app.post("/login")
async def login(response: Response, db: Session = Depends(get_db_pg), username=Form(...), password=Form(...)):
    
    user_login = db.query(UserDetails).filter(UserDetails.username == username).first()

    if not user_login or not verify_password(password, user_login.password):
        raise  HTTPException(status_code=404, detail="Invalid login details")
    
    access_token = create_access_token(data={"sub": user_login.username})
    refresh_token = create_refresh_token(data={"sub": user_login.username})
    
    #set httpOnly cookies
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    return {"message": "Login successful"}

@app.post("/refresh-token")
async def refresh_token(response: Response, refresh_token: str = Cookie(None)):
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    username = payload.get("sub")
    new_access_token = create_access_token({"sub": username})

    response.set_cookie(key="access_token", value=new_access_token, httponly=True)

    return {"message": "Access token refreshed"}





#----------------------------DONE----------------------------
#Create Post (Form + File Upload + Background Task)
@app.post("/upload")
async def upload_file(db: Session = Depends(get_db_sqlite),  
                      title: str = Form(...), content: str = Form(...), 
                      image: UploadFile = File(...), author: str = Form(...),
                     _: str = Depends(get_current_user)):
     
    file_location = os.path.join(Upload_dir, image.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(image.file, f)

    user_information = PostSchema(
        title = title,
        content = content,
        author = author,
        fileName = image.filename
    )

    # db_posts = posts(author = author, title = title, content = content, fileName = image.filename)
    db_posts = posts(**user_information.model_dump())
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
                    _: str = Depends(get_current_user)):
    
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
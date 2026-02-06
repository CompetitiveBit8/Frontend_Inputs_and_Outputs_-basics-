from fastapi import Depends, FastAPI, Response, Request, Form, UploadFile, File, BackgroundTasks, Query, HTTPException, Cookie
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from app.db.database import get_db_sqlite_old, sessionLocal, sessionLocal_sqlite,  Base_sqlite, Base, engine_sqlite, Base_sqlite_old, engine_sqlite_old, engine, get_db, get_db_sqlite, get_db_sqlite_old, Base_sqlite_old
from app.models.models import UserDetails, posts_old, posts, images
from app.schema.schema import UserLogin, PostSchema, ImageSchema
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.utils.auth_utils import hash_password, verify_password, create_access_token, decode_access_token, create_refresh_token, decode_refresh_token, get_current_user
import os
import shutil
from typing import Optional
from datetime import timedelta
import requests


#creating tables
Base_sqlite.metadata.create_all(bind=engine_sqlite)
Base.metadata.create_all(bind=engine)
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
async def signup(username=Form(...), password=Form(...), db: Session = Depends(get_db)):
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
async def login(response: Response, db: Session = Depends(get_db), username=Form(...), password=Form(...)):
    
    user_login = db.query(UserDetails).filter(UserDetails.username == username).first()

    if not user_login or not verify_password(password, user_login.password):
        raise  HTTPException(status_code=404, detail="Invalid login details")
    
    access_token = create_access_token(data={"sub": user_login.username})
    refresh_token = create_refresh_token(data={"sub": user_login.username})
    
    #set httpOnly cookies
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    print("/n/n Login Successful /n/n")
    return {"message": "Login successful"}



@app.post("/refresh")
async def refresh_token(response: Response, refresh_token: str = Cookie(None)):

    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    payload = decode_refresh_token(refresh_token)
    if payload is None: 
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Create NEW access token
    new_access_token = create_access_token({"sub": username})
    
    # Create NEW refresh token (token rotation)
    new_refresh_token = create_refresh_token(
        {"sub": username}, 
        expires_delta=timedelta(days=3)
    )

    # Set both cookies
    response.set_cookie(
        key="access_token", 
        value=new_access_token, 
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    
    response.set_cookie(
        key="refresh_token", 
        value=new_refresh_token, 
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )

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


    db_image = images(
        file_path=file_location,
        file_name=image.filename,
        file_type=image.content_type
    )

    post_information = PostSchema(
        title = title,
        content = content,
        author = author,
    )

    db_posts = posts(**post_information.model_dump())
    db.add_all([db_posts, db_image])
    db.commit()
    return {"messages" : "post updated"}


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



@app.get("/image/{post_id}/download")
async def download_image(post_id: int, db: Session = Depends(get_db_sqlite),
                         _: str = Depends(get_current_user)):

    path_query = (
        db.query(images)
        .filter(images.id == post_id)
        .first()
    )

    if not path_query:
        raise HTTPException(status_code=404, detail="Image does not exist on that ID")

    image_path = path_query.file_path

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="File missing on server")

    return FileResponse(
        path=image_path,
        media_type=path_query.file_type,
        filename=path_query.file_name
    )

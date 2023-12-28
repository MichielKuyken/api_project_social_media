from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import crud
import models
import schemas
from database import SessionLocal, engine
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import auth

if not os.path.exists('.\sqlitedb'):
    os.makedirs('.\sqlitedb')

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


security = HTTPBasic()


origins = [
    "https://michielkuyken.github.io/fomula1_api.github.io/",
    "file:///C:/Users/Eigenaar/Documents/2CCS/API%20development/API%20website/index.html"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_scheme_admin = OAuth2PasswordBearer(tokenUrl="token")
print(oauth2_scheme_admin)


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    admin = auth.authenticate_admin(db, form_data.username, form_data.password)
    print(user)
    print(admin)
    if not user and not admin:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user:
        access_token = auth.create_access_token(
            data={"sub": user.username}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    elif admin:
        access_token_admin = auth.create_access_token(
            data={"sub": admin.username}
        )
        return {"access_token_admin": access_token_admin, "token_type": "bearer"}


@app.post("/admin/")
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    login = crud.get_admin_by_username(db, username=admin.username)
    if login:
        raise HTTPException(status_code=400, detail="Admin already registred")
    return crud.create_admin(db=db, admin=admin)


@app.get("/admin/{admin_username}", response_model=schemas.Admin)
def read_admin(admin_username: str, db: Session = Depends(get_db)):
    admin = crud.get_admin_by_username(db, username=admin_username)
    return admin


@app.delete("/admin/{admin_username}")
def delete_team(admin_username: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    print(token)
    current_admin = auth.get_current_admin(db, token)
    if not current_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    if current_admin != admin_username:
        raise HTTPException(status_code=404, detail="Admin not found")
    return crud.delete_admin(db=db, admin=current_admin)


@app.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user_username = crud.get_user(db, username=user.username)
    if user_username:
        raise HTTPException(status_code=400, detail="Username already registred")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{username}", response_model=schemas.User)
def read_user(user_username: str, db: Session = Depends(get_db)):
    user = crud.get_user(db, username=user_username)
    if user_username is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/users/{username}")
def delete_user(username: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = auth.get_current_user(db, token)
    current_admin = auth.get_current_admin(db, token)
    if not current_user and not current_admin:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud.get_user(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db=db, user=user)


@app.put("/users/", response_model=schemas.User)
def update_user(user_update: schemas.UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = auth.get_current_user(db, token)
    current_admin = auth.get_current_admin(db, token)
    if not current_user and not current_admin:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = crud.update_user(db, current_user, user_update)
    return updated_user


@app.post("/posts/")
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = auth.get_current_user(db, token)
    current_admin = auth.get_current_admin(db, token)
    if not current_user and not current_admin:
        raise HTTPException(status_code=404, detail="User not found")
    post_titel = crud.get_post(db, post_titel=post.titel)
    if post_titel:
        raise HTTPException(status_code=400, detail="Titel already used")
    return crud.create_post(db=db, post=post, user_id=current_user.id)


@app.get("/", response_model=list[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = crud.get_posts(db, skip=skip, limit=limit)
    return posts


@app.get("/posts/{titel}", response_model=schemas.Post)
def read_posts_by_titel(post_titel: str, db: Session = Depends(get_db)):
    posts = crud.get_post(db, post_titel=post_titel)
    if post_titel is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return posts


@app.delete("/posts/{titel}")
def deleteposttype(titel: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = auth.get_current_user(db, token)
    if not current_user:
        print("hello")
        current_admin = auth.get_current_admin(db, token)
        print("hello")
    post = crud.get_post(db, post_titel=titel)
    print(post.titel)
    if current_user.id != post.user_id:
        raise HTTPException(status_code=401, detail="User does not own post")
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return crud.delete_post(db=db, post=post)


@app.put("/posts/{post_id}")
def update_post(post_update: schemas.PostCreate, post_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = auth.get_current_user(db, token)
    current_admin = auth.get_current_admin(db, token)
    if not current_user and not current_admin:
        raise HTTPException(status_code=404, detail="User not found")
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    updated_post = crud.update_post(db, post, post_update)
    return updated_post


@app.post("/types/")
def create_types(types: schemas.TypeCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_admin = auth.get_current_admin(db, token)
    if not current_admin:
        raise HTTPException(status_code=404, detail="User not found")
    typename = crud.get_type(db, typename=types.type_naam)
    if typename:
        raise HTTPException(status_code=400, detail="Type name already registred")
    return crud.create_type(db=db, types=types)


@app.get("/types/", response_model=list[schemas.Type])
def read_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    types = crud.get_types(db, skip=skip, limit=limit)
    return types


@app.get("/types/{type_id}", response_model=schemas.Type)
def read_type(type_id: int, db: Session = Depends(get_db)):
    types = crud.get_type_by_id(db, type_id=type_id)
    if types is None:
        raise HTTPException(status_code=404, detail="Type not found")
    return types


@app.delete("/types/{typename}")
def delete_type(typename: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_admin = auth.get_current_admin(db, token)
    if not current_admin:
        raise HTTPException(status_code=404, detail="User not found")
    types = crud.get_type(db, typename=typename)
    if not types:
        raise HTTPException(status_code=404, detail="Type not found")
    return crud.delete_type(db=db, types=types)


@app.put("/types/{type_id}")
def update_type(type_update: schemas.TypeCreate, type_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_admin = auth.get_current_admin(db, token)
    if not current_admin:
        raise HTTPException(status_code=404, detail="User not found")
    types = crud.get_type_by_id(db, type_id=type_id)
    if not types:
        raise HTTPException(status_code=404, detail="Type not found")
    updated_type = crud.update_type(db, types, type_update)
    return updated_type




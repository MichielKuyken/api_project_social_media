from sqlalchemy.orm import Session

import models
import schemas
import auth


def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, password=hashed_password, voornaam=user.voornaam, achternaam=user.achternaam, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return "User successfully created!"


def delete_user(db: Session, user: schemas.User):
    db.delete(user)
    db.commit()
    return "User successfully deleted"


def update_user(db: Session, existing_user: models.User, user_update: schemas.UserCreate):
    for key, value in user_update.dict().items():
        setattr(existing_user, key, value)
    db.commit()
    db.refresh(existing_user)
    return existing_user


def get_post(db: Session, post_titel: str):
    return db.query(models.Post).filter(models.Post.titel == post_titel).first()


def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()


def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    print(user_id)
    db_post = models.Post(titel=post.titel, text=post.text, date=post.date, user_id=user_id, type_id=post.type_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return "Post successfully created!"


def delete_post(db: Session, post: schemas.Post):
    db.delete(post)
    db.commit()
    return "Post successfully deleted!"


def update_post(db: Session, existing_post: models.Post, post_update: schemas.PostCreate):
    for key, value in post_update.dict().items():
        setattr(existing_post, key, value)
    db.commit()
    db.refresh(existing_post)
    return "Post successfully updated!"


def get_type(db: Session, typename: str):
    return db.query(models.Type).filter(models.Type.type_naam == typename).first()


def get_type_by_id(db: Session, type_id: int):
    return db.query(models.Type).filter(models.Type.id == type_id).first()


def get_types(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Type).offset(skip).limit(limit).all()


def create_type(db: Session, types: schemas.TypeCreate):
    db_type = models.Type(**types.dict())
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return "Type successfully created!"


def delete_type(db: Session, types: schemas.Type):
    db.delete(types)
    db.commit()
    return "Type successfully deleted!"


def update_type(db: Session, existing_type: models.Type, type_update: schemas.TypeCreate):
    for key, value in type_update.dict().items():
        setattr(existing_type, key, value)
    db.commit()
    db.refresh(existing_type)
    return "Type successfully updated!"


def get_admin(db: Session):
    return db.query(models.Admin).first()


def get_admin_by_username(db: Session, username: str):
    return db.query(models.Admin).filter(models.Admin.username == username).first()


def delete_admin(db: Session, admin: schemas.Admin):
    db.delete(admin)
    db.commit()
    return "Admin successfully deleted"


def create_admin(db: Session, admin: schemas.AdminCreate):
    if len(db.query(models.Admin).all()) == 0:
        hashed_password = auth.get_password_hash(admin.password)
        db_admin = models.Admin(username=admin.username, password=hashed_password)
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        return "Admin successfully created"

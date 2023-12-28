from passlib.context import CryptContext
import crud
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_scheme_admin = OAuth2PasswordBearer(tokenUrl="token")
print(oauth2_scheme_admin)
SECRET_KEY = "F73F0C493C83FEE28BA5E7CFA4071CFF96988D845B20E382E083A1E0F15632C7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def authenticate_admin(db: Session, username: str, password: str):
    admin = crud.get_admin_by_username(db, username)
    if not admin:
        return False
    if not verify_password(password, admin.password):
        return False
    return admin


def create_access_token(data: dict):
    to_encode = data.copy()
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default to 15 minutes of expiration time if ACCESS_TOKEN_EXPIRE_MINUTES variable is empty
        expire = datetime.utcnow() + timedelta(minutes=15)
    # Adding the JWT expiration time case
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(db: Session, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload is None:
            return None
        username_user: str = payload.get("sub")
        if username_user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user(db, username_user)
    if user is None:
        raise credentials_exception
    return user


def get_current_admin(db: Session, token_admin: str = Depends(oauth2_scheme_admin)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print("check")
    print(token_admin)
    try:
        print("check")
        payload = jwt.decode(token_admin, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    admin = crud.get_admin_by_username(db, username=username)
    if admin is None:
        raise credentials_exception
    return admin

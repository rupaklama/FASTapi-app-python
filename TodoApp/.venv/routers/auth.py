from fastapi import APIRouter
from pydantic import BaseModel, Field

import os
from datetime import datetime, timedelta, timezone

# Import for database session management
# depends is used for dependency injection in FastAPI
from fastapi import Depends, HTTPException, status

from models import Users

# passlib is a password hashing library
from passlib.context import CryptContext

# Import necessary modules for dependency injection and type annotations
from typing import Annotated


from sqlalchemy.orm import Session

# Import the engine to create the database tables
from database import SessionLocal

# OAuth2PasswordRequestForm is secure and standard for handling user login forms
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

# jose is a library for handling JSON Web Tokens (JWT)
from jose import JWTError, jwt

from dotenv import load_dotenv

# Create a router for authentication-related endpoints to be used in the main app
# ApiRouter allows you to organize your FastAPI application into smaller, manageable modules
# It will allows us to route from our main.py file to this auth.py file
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# Create a password context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction from requests
# This will be used to secure endpoints that require authentication
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")

# pydantic model for user creation request validation can be added here
class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$')
    first_name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    role: str = Field(..., min_length=2)
    

class Token(BaseModel):
    access_token: str
    token_type: str
    

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        # Yields a database session to be used in request handling
        # and ensures the session is closed after the request is done
        yield db
    finally:
        db.close()

# set up a reusable way to inject a database session into your FastAPI routes
# a type annotation and dependency declaration commonly used in FastAPI applications that utilize SQLAlchemy for database access
db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


# Ensure JWT settings are loaded before decoding the token
load_dotenv()
jwt_secret_key = os.getenv("JWT_SECRET_KEY")
jwt_algorithm = os.getenv("JWT_ALGORITHM")
    
def create_access_token(username: str, user_id: int, expires_delta: timedelta = 15):
    to_encode = {"sub": username, "id": user_id}
    
    if not jwt_secret_key:
        raise EnvironmentError("JWT_SECRET_KEY not found in .env")

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_secret_key, algorithm=jwt_algorithm)
    return encoded_jwt


# Verify and get the current user from the token
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency):
    try:
        payload = jwt.decode(token, jwt_secret_key, algorithms=[jwt_algorithm])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        user = db.query(Users).filter(Users.id == user_id).first()
        return user
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        ) from exc


@router.post("/", status_code=201)
async def create_user(user: UserCreateRequest, db: db_dependency):
    user_model = Users(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        hashed_password=pwd_context.hash(user.password),
        role=user.role,
        is_active=True
    )
    db.add(user_model)
    db.commit()
    db.refresh(user_model)
    return {"message": "User created successfully", "user": user_model.username}

@router.post("/login", response_model=Token)
# Annotated type is used to combine type hints with additional metadata
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return {"error": "Invalid username or password"}

    token = create_access_token(username=form_data.username, user_id=user.id)
    return {"access_token": token, "token_type": "bearer"}

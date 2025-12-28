from fastapi import APIRouter, HTTPException

# Import for database session management
# depends is used for dependency injection in FastAPI
from fastapi import Depends

from pydantic import BaseModel, Field


# Import necessary modules for dependency injection and type annotations
from typing import Annotated


from sqlalchemy.orm import Session

# Ensure models are imported so that they are registered with the ORM
import models
# Import the engine to create the database tables
from database import SessionLocal

from routers.auth import router

from routers.auth import get_current_user

router = APIRouter()


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

# Dependency to get the current authenticated user
user_dependency = Annotated[models.Users, Depends(get_current_user)]

# Define the Pydantic model for request validation
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    completed: bool = Field(default=False)

@router.get("/")
async def read_all(db: db_dependency):
    return db.query(models.Todo).all()

@router.get("/todo/{todo_id}")
async def read_todo(todo_id: int, db: db_dependency):
    todo_model = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")

@router.post("/todo/", status_code=201)
async def create_todo(user: user_dependency, todo_request: TodoRequest, db: db_dependency):
    # .dict() method converts the Pydantic model into a standard Python dictionary, where each key-value pair corresponds to a field and its value
    # ** operator unpacks this dictionary so that each key-value pair is passed as a keyword argument to the models
    
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    
    todo_model = models.Todo(**todo_request.dict(), owner_id=user.id)
    # todo_model = models.Todo()
    # todo_model.title = todo_request.title
    # todo_model.description = todo_request.description
    # todo_model.priority = todo_request.priority
    # todo_model.completed = todo_request.completed

    # Add the new todo item to the database session and commit the transaction
    db.add(todo_model)
    db.commit()

    return {
        "id": todo_model.id, 
        "title": todo_model.title,
        "description": todo_model.description,
        "priority": todo_model.priority,
        "completed": todo_model.completed
    }
    
@router.put("/todo/{todo_id}", status_code=200)
async def update_todo(todo_id: int, todo_request: TodoRequest, db: db_dependency):
    todo_model = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.completed = todo_request.completed

    db.add(todo_model)
    db.commit()

    return todo_model

@router.delete("/todo/{todo_id}", status_code=200)
async def delete_todo(todo_id: int, db: db_dependency):
    todo_model = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo_model)
    db.commit()

    return todo_model

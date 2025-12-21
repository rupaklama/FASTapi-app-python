from fastapi import FastAPI

# Import necessary modules for dependency injection and type annotations
from typing import Annotated


# Ensure models are imported so that they are registered with the ORM
import models
# Import the engine to create the database tables
from database import engine

from routers import auth, todos

app = FastAPI()

# Create the database tables
models.Base.metadata.create_all(bind=engine)

# import and include the routers for endpoints
# This allows the main app to use the routes defined in the auth and todos modules
app.include_router(auth.router)
app.include_router(todos.router)


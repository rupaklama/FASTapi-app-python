# create an engine that will interact with the SQLite database specified by the URL.
from sqlalchemy import create_engine

# import sessionmaker to create a configured "Session" class.
# A session in SQLAlchemy is used to manage the operations on the database.
from sqlalchemy.orm import sessionmaker

# import declarative_base to create a base class for our ORM models.
from sqlalchemy.ext.declarative import declarative_base

# ./todos.db means the database file will be created (or accessed) in the current working directory, 
# with the filename todos.db.
SQLAlCHEMY_DATABASE_URL = "sqlite:///./todos.db"

# The connect_args parameter is specific to SQLite. 
# It is used to pass additional arguments to the database connection.
# In this case, {"check_same_thread": False} is used to allow the database connection
# to be shared across multiple threads, which is important for web applications that handle multiple requests concurrently.
engine = create_engine(
    SQLAlCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# sessionmaker is a factory for creating new Session objects.
# The bind=engine argument associates the sessions created by this sessionmaker with the previously defined engine.
# The autocommit=False argument means that changes to the database will not be automatically committed.
# The autoflush=False argument means that changes to the database will not be automatically flushed to the database.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is a base class for our ORM models.
Base = declarative_base()


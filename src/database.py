from .config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

#connects to database through SQLalchemy
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.create_all(engine)

# default values
SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind = engine)

  

# session object creates a session with the database, letting us send SQL statements to it
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from sqlalchemy import create_engine
from app.config.config import settings
from sqlalchemy.orm import declarative_base, sessionmaker

#--------Postgress Connection--------
DATABASE_URL_PG = settings._link
engine = create_engine(DATABASE_URL_PG)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


#--------SQLite Connection---------

DATABASE_URL_SQLITE = settings.sq_link
engine_sqlite = create_engine(DATABASE_URL_SQLITE, connect_args={"check_same_thread": False})
sessionLocal_sqlite = sessionmaker(autocommit=False, autoflush=False, bind=engine_sqlite)
Base_sqlite = declarative_base()

def get_db_sqlite():
    db = sessionLocal_sqlite()
    try:
        yield db
    finally:
        db.close()

#----------New SQLite Connection----------

DATABASE_URL_SQLITE = settings.sq_link_old
engine_sqlite_old = create_engine(DATABASE_URL_SQLITE, connect_args={"check_same_thread": False})
sessionLocal_sqlite_old = sessionmaker(autocommit=False, autoflush=False, bind=engine_sqlite_old)
Base_sqlite_old = declarative_base()

def get_db_sqlite_old():
    db_old = sessionLocal_sqlite_old()
    try:
        yield db_old
    finally:
        db_old.close()
from sqlalchemy import create_engine
from app.config.config import settings
from sqlalchemy.orm import declarative_base, sessionmaker

#--------Postgress Connection--------
DATABASE_URL_PG = settings.pg_link
# DATABASE_URL_PG = "sqlite:///./test_pg.db"
engine_pg = create_engine(DATABASE_URL_PG)
sessionLocal_pg = sessionmaker(autocommit=False, autoflush=False, bind=engine_pg)
Base_pg = declarative_base()

def get_db_pg():
    db = sessionLocal_pg()
    try:
        yield db
    finally:
        db.close()


#--------SQLite Connection---------

DATABASE_URL_SQLITE = "sqlite:///posts.db"
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

DATABASE_URL_SQLITE = "sqlite:///posts_old.db"
engine_sqlite_old = create_engine(DATABASE_URL_SQLITE, connect_args={"check_same_thread": False})
sessionLocal_sqlite_old = sessionmaker(autocommit=False, autoflush=False, bind=engine_sqlite_old)
Base_sqlite_old = declarative_base()

def get_db_sqlite_old():
    db_old = sessionLocal_sqlite_old()
    try:
        yield db_old
    finally:
        db_old.close()
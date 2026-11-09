from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import DB_URL


class Base(DeclarativeBase):
    pass


engine = create_engine(DB_URL, echo=False)

@event.listens_for(engine, "connect")
def _enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

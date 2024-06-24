from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    token = Column(String, unique=True, index=True)


class ImageRecord(Base):
    __tablename__ = "image_records"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.now)
    image_url = Column(String, index=True)
    file_url = Column(String, index=True)
    status = Column(String, index=True)

    @hybrid_property
    def full_image_url(self):
        return f"{os.getenv('HOST')}/{self.image_url}"

    @hybrid_property
    def full_file_url(self):
        return f"{os.getenv('HOST')}/{self.file_url}"
    

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    
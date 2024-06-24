# models.py
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserRead(UserBase):
    id: int
    token: str

class UserInDB(UserBase):
    hashed_password: str
    token: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str



class ImageRecordBase(BaseModel):
    date: datetime
    full_file_url: HttpUrl
    full_image_url: HttpUrl
    status: str

class ImageRecordCreate(ImageRecordBase):
    pass

class ImageRecordRead(ImageRecordBase):
    id: int

    class Config:
        orm_mode = True

class ImageBase64(BaseModel):
    base64_string: str

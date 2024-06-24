# main.py
from fastapi import FastAPI, Depends, HTTPException, status, Header, UploadFile, File, status, BackgroundTasks
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from secrets import token_urlsafe
from models import UserCreate, UserRead, UserLogin, ImageRecordRead, ImageRecordCreate, ImageBase64
from database import SessionLocal, engine, Base, User, ImageRecord
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException
import shutil
from tasks import image_to_text
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime



Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/files", StaticFiles(directory="files"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_token():
    return token_urlsafe(32)

def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = db.query(User).filter(User.token == authorization).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/register/", response_model=UserRead)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    token = create_token()
    db_user = User(email=user.email, name=user.name, hashed_password=hashed_password, token=token)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/login/", response_model=UserRead)
def login_user(user:UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return db_user

@app.get("/users/me/", response_model=UserRead)
def read_users_me(authorization: str = Header(...), db: Session = Depends(get_db)):
    token = authorization.split(" ")[1] if " " in authorization else authorization
    db_user = db.query(User).filter(User.token == token).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return db_user



@app.post('/upload/')
def upload_image(image: ImageBase64, db: Session = Depends(get_db)):
    try:
        # Decode the base64 string
        image_data = base64.b64decode(image.base64_string)
        # Convert the bytes to a PIL image
        image = Image.open(BytesIO(image_data))

        # Define the path to save the image
        path = f"files/{int(datetime.now().timestamp())}.png"
        image.save(path)

        # Prepare the record to be inserted into the database
        image_to_db = {
            "image_url": path,
            "file_url": "",
            "status": "processing"
        }

        # Create a new database record
        db_record = ImageRecord(**image_to_db)
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        print(db_record.id)
        # Process the image (e.g., extract text from image)
        t = image_to_text(path, db_record.id)

        return {
            'file': "uploaded_image.png",
            'content': "image/png",
            'path': path,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {e}")



@app.get("/reports/", response_model=List[ImageRecordRead])
def read_image_records(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    records = db.query(ImageRecord).offset(skip).limit(limit).all()
    return records
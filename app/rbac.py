from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, constr

# Constants
DATABASE_URL = "sqlite:///./role_based_app.db"
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database setup
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    access_levels = Column(String, nullable=False)  # Comma-separated roles allowed

# Pydantic schemas
class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)
    role: constr(min_length=3, max_length=20)

class UserLogin(BaseModel):
    username: str
    password: str

class ResourceCreate(BaseModel):
    name: str
    access_levels: str  # Comma-separated roles

class ResourceOut(BaseModel):
    id: int
    name: str
    access_levels: str

    class Config:
        orm_mode = True

# Utility functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_user(db: Session, username: str, password: str, role: str):
    hashed_password = pwd_context.hash(password)
    user = User(username=username, hashed_password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# FastAPI app
app = FastAPI()

# Routes
@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if user.role not in ["user", "admin", "super_admin"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    created_user = create_user(db, user.username, user.password, user.role)
    return {"message": "User registered successfully", "user_id": created_user.id}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    authenticated_user = authenticate_user(db, user.username, user.password)
    if not authenticated_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": authenticated_user.username, "role": authenticated_user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/resources", response_model=list[ResourceOut])
def get_resources(token: str = Depends(), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if not role:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    resources = db.query(Resource).all()
    accessible_resources = [r for r in resources if role in r.access_levels.split(",")]
    return accessible_resources

@app.post("/resources")
def create_resource(resource: ResourceCreate, token: str = Depends(), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if role != "super_admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    new_resource = Resource(name=resource.name, access_levels=resource.access_levels)
    db.add(new_resource)
    db.commit()
    return {"message": "Resource created successfully"}

# Create database tables
Base.metadata.create_all(bind=engine)

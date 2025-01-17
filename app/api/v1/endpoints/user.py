from fastapi import APIRouter, HTTPException, Depends
from app.db.base import get_db
from app.db.models.user import User
from sqlalchemy.orm import Session
from app.db.schemas.user import UserCreate, UserLogin
from app.services.auth_service import authenticate_user, create_access_token, get_current_user
from app.services.user_service import create_user

router = APIRouter()

@router.post("/register", tags=["User"])
async def register(user: UserCreate, db: Session = Depends(get_db)):
    return await create_user(user, db)

# Route to get JWT token for user login
@router.post("/token", tags=["User"])
async def login(user: UserLogin, db: Session = Depends(get_db)):
    email = user.email
    password = user.password
    
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

# Route to fetch details of the current authenticated user
@router.get("/users/me")
async def read_users_me(current_user=Depends(get_current_user)):
    return current_user

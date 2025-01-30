from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class LoginRequest(BaseModel):
    username: str
    password: str
    
# Signup request model
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    
class ConfirmRequest(BaseModel):
    email: EmailStr
    code: str
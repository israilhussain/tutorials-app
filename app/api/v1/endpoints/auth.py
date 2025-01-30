from fastapi import APIRouter
from app.db.schemas.user import ConfirmRequest, LoginRequest, SignupRequest
from app.services.cognito_auth_service import cognito_confirm_user_service, cognito_login_service, cognito_signup_service

router = APIRouter()

@router.post("/login")
def login(request: LoginRequest):
    return cognito_login_service(request)

@router.post("/signup")
def signup(request: SignupRequest):
    return cognito_signup_service(request)

@router.post("/confirm")
def confirm_user(request: ConfirmRequest):
    return cognito_confirm_user_service(request)


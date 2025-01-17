from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import pyotp
import qrcode
import io

router = APIRouter()

# Base32 secret for TOTP
SECRET_KEY = "base32secret3232"

@router.get("/generate-qr", response_class=StreamingResponse)
async def generate_qr(username: str):
    """
    Generate and return a QR code for setting up TOTP in an authenticator app.
    - `username`: The user's email or unique identifier.
    """
    # Generate TOTP provisioning URI
    totp = pyotp.TOTP(SECRET_KEY)
    qr_code_url = totp.provisioning_uri(username, issuer_name="MyApp")

    # Generate QR code image
    qr_image = qrcode.make(qr_code_url)
    img_buffer = io.BytesIO()
    qr_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # Return the QR code image as a streaming response
    return StreamingResponse(img_buffer, media_type="image/png")




# from fastapi import FastAPI
# from fastapi.responses import StreamingResponse

# app = FastAPI()

# def generate_totp_secret(user_id: str):
#     totp = pyotp.TOTP(pyotp.random_base32())
#     provisioning_uri = totp.provisioning_uri(user_id, issuer_name="YourEnterpriseApp")
#     return totp, provisioning_uri

# def serve_qr_code(uri: str):
#     qr = qrcode.make(uri)
#     buf = BytesIO()
#     qr.save(buf)
#     buf.seek(0)
#     return StreamingResponse(buf, media_type="image/png")

# @app.get("/generate-qr/{user_id}")
# def generate_qr(user_id: str):
#     _, provisioning_uri = generate_totp_secret(user_id)
#     return serve_qr_code(provisioning_uri)


# Note this a authentication based on email, password and then TOTP (if MFA enabled)

# from fastapi import FastAPI, HTTPException, Depends
# from pydantic import BaseModel
# from jose import JWTError, jwt
# import pyotp
# from datetime import datetime, timedelta

# app = FastAPI()

# # In-memory user database
# users_db = {
#     "user@example.com": {
#         "password": "hashed_password",  # Replace with hashed password in production
#         "totp_secret": pyotp.random_base32(),  # Only for MFA-enabled users
#         "mfa_enabled": True,
#     },
#     "user2@example.com": {
#         "password": "another_hashed_password",
#         "totp_secret": None,
#         "mfa_enabled": False,
#     },
# }

# # JWT configuration
# SECRET_KEY = "your_jwt_secret"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # Pydantic models
# class LoginRequest(BaseModel):
#     email: str
#     password: str

# class TOTPRequest(BaseModel):
#     email: str
#     totp_code: str

# class TokenResponse(BaseModel):
#     access_token: str
#     token_type: str

# class MFAResponse(BaseModel):
#     message: str
#     mfa_required: bool

# # Utility: Create a JWT token
# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# # Step 1: Email and Password Login
# @app.post("/login", response_model=MFAResponse)
# async def login(request: LoginRequest):
#     user = users_db.get(request.email)
#     if not user or user["password"] != request.password:  # Replace with secure hash check
#         raise HTTPException(status_code=401, detail="Invalid email or password")

#     if user["mfa_enabled"]:
#         return {"message": "MFA required", "mfa_required": True}

#     # If MFA is not enabled, directly issue a token
#     access_token = create_access_token({"sub": request.email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     return {"message": "Login successful", "mfa_required": False, "access_token": access_token}

# # Step 2: TOTP Verification
# @app.post("/login-totp", response_model=TokenResponse)
# async def verify_totp(request: TOTPRequest):
#     user = users_db.get(request.email)
#     if not user or not user["mfa_enabled"]:
#         raise HTTPException(status_code=400, detail="MFA not enabled for this user")

#     totp = pyotp.TOTP(user["totp_secret"])
#     if not totp.verify(request.totp_code):
#         raise HTTPException(status_code=401, detail="Invalid TOTP code")

#     # Issue a token after successful TOTP verification
#     access_token = create_access_token({"sub": request.email}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     return {"access_token": access_token, "token_type": "bearer"}

import os
import boto3
from fastapi import HTTPException
from app.db.schemas.user import ConfirmRequest, LoginRequest, SignupRequest
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID")

client = boto3.client("cognito-idp", aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION)


def cognito_login_service(request: LoginRequest):
    try:
        response = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": request.username,
                "PASSWORD": request.password
            },
            ClientId=CLIENT_ID
        )
        return {"token": response["AuthenticationResult"]["IdToken"]}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    
def cognito_signup_service(request: SignupRequest):
    try:
        response = client.sign_up(
            ClientId=CLIENT_ID,
            Username=request.email,
            Password=request.password,
            UserAttributes=[
                {"Name": "email", "Value": request.email},
                {"Name": "name", "Value": request.name}
            ]
        )
        print("cognito_signup_service response: ", response)
        return {"message": "User registered successfully. Please check your email for confirmation."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
def cognito_confirm_user_service(request: ConfirmRequest):
    try:
        response = client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=request.email,
            ConfirmationCode=request.code
        )
        print("cognito_confirm_user_service response: ", response)
        return {"message": "User confirmed successfully. You can now log in."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

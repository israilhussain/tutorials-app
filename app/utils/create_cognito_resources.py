import boto3 # type: ignore
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

def create_cognito_resources():
    cognito = boto3.client(
        "cognito-idp",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

    # Step 1: Create a User Pool
    user_pool = cognito.create_user_pool(
        PoolName="MyUserPool",
        Policies={
            "PasswordPolicy": {
                "MinimumLength": 8,
                "RequireUppercase": True,
                "RequireLowercase": True,
                "RequireNumbers": True,
                "RequireSymbols": False,
            }
        },
        AutoVerifiedAttributes=["email"],  # Auto-verify email
        AdminCreateUserConfig={"AllowAdminCreateUserOnly": False},
    )
    user_pool_id = user_pool["UserPool"]["Id"]
    print(f"User Pool ID: {user_pool_id}")

    # Step 2: Create an App Client
    app_client = cognito.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName="MyAppClient",
        GenerateSecret=False,
        ExplicitAuthFlows=[
            "ALLOW_USER_PASSWORD_AUTH",
            "ALLOW_REFRESH_TOKEN_AUTH",
            "ALLOW_CUSTOM_AUTH",
        ],
        AllowedOAuthFlows=[
            "code",  # For authorization code grant
            "implicit"  # For implicit grant
        ],
        AllowedOAuthScopes=[
            "openid",  # Enables ID Token generation
            "email",
            "profile",
            "aws.cognito.signin.user.admin",
        ],
        CallbackURLs=[
            "http://localhost:3000/callback"  # Add your app's redirect URI
        ],
        LogoutURLs=[
            "http://localhost:3000/logout"  # Add your app's logout URI
        ]
    )
    app_client_id = app_client["UserPoolClient"]["ClientId"]
    print(f"App Client ID: {app_client_id}")

    return user_pool_id, app_client_id

if __name__ == "__main__":
    create_cognito_resources()

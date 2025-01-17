from fastapi import APIRouter, Request
from authlib.integrations.starlette_client import OAuth
import os

# import dotenv

# dotenv.load_dotenv()

AUTH0_CLIENT_ID="YeNqXAo3VIzFaaVPgFTi2KNnCFtcrqXU"
AUTH0_CLIENT_SECRET="FUam-3BqWlkN7M0MZAnjWpyFzAMfN4m2yQ0EPczPpLEoPUMNufVMB04LW774QBZQ"
YOUR_AUTH0_DOMAIN="dev-ik6pjv551ifjn6il.us.auth0.com"

router = APIRouter()

oauth = OAuth()
oauth.register(
    name='auth0',
    client_id=AUTH0_CLIENT_ID,  # Auth0 Client ID
    client_secret=AUTH0_CLIENT_SECRET,  # Auth0 Client Secret
    server_metadata_url=f"https://{YOUR_AUTH0_DOMAIN}/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)

@router.get("/login")
async def login(request: Request):
    print(os.getenv('YOUR_AUTH0_DOMAIN'))

    redirect_uri = request.url_for("auth")  # Redirect URL for Auth0
    # return redirect_uri
    return await oauth.auth0.authorize_redirect(request, redirect_uri)

@router.get("/auth")
async def auth(request: Request):
    token = await oauth.auth0.authorize_access_token(request)
    user_info = token.get("userinfo")
    return {"access_token": token["access_token"], "user_info": user_info}


# you will find all the api info here. Nice thing to know about.
# https://dev-ik6pjv551ifjn6il.us.auth0.com/.well-known/openid-configuration
from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from starlette.responses import RedirectResponse
from starlette.config import Config
import os
from dotenv import load_dotenv

load_dotenv()

config = Config(".env")
oauth = OAuth(config)

google = oauth.register(
    name="google",
    client_id=config("CLIENT_ID"),
    client_secret=config("CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email"},
)


# ✅ AHORA RECIBE request OBLIGATORIAMENTE
async def login_google(request: Request):
    redirect_uri = os.getenv("APP_URL") + "/auth/callback"
    return await google.authorize_redirect(request, redirect_uri)


async def auth_callback(request: Request):
    token = await google.authorize_access_token(request)
    user_info = token["userinfo"]

    request.session["user"] = {
        "email": user_info["email"],
        "token": token["access_token"]
    }

    return RedirectResponse(f"/map/{user_info['email']}")


def get_current_user(request: Request):
    return request.session.get("user")

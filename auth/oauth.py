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
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}, # 'profile' para obtener el nombre
)

async def login_google(request: Request):
    # En producción (Vercel) esto debe ser la URL real, en local localhost
    # Usamos request.url_for para que se adapte automático
    redirect_uri = request.url_for('callback') 
    return await google.authorize_redirect(request, redirect_uri)

async def auth_callback(request: Request):
    token = await google.authorize_access_token(request)
    user_info = token.get("userinfo")
    
    if not user_info:
        # Fallback si userinfo no viene directo en el token
        user_info = await google.userinfo(token=token)

    request.session["user"] = {
        "email": user_info["email"],
        "name": user_info.get("name", "Usuario Anónimo"),
        "token": token["access_token"] # Guardamos token para auditoría
    }

    return RedirectResponse("/")

def get_current_user(request: Request):
    return request.session.get("user")
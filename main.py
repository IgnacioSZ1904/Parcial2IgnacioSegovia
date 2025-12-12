from fastapi import FastAPI, Request, Form, UploadFile, Depends, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from auth.oauth import login_google, auth_callback, get_current_user
from database.database import db
from services.mapa import geocode
from services.imagen import upload_image
from datetime import datetime
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configuración
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "examen_secret"))
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- AUTH ---
@app.get("/auth/login")
async def login(request: Request):
    return await login_google(request)

@app.get("/auth/callback")
async def callback(request: Request):
    return await auth_callback(request)

@app.get("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)

# --- RUTAS PRINCIPALES ---

@app.get("/", response_class=HTMLResponse)
async def root(request: Request, user=Depends(get_current_user)):
    # Requisito: No se puede usar sin identificarse
    if not user:
        return RedirectResponse("/auth/login")

    # Recuperar todas las reseñas (globales)
    reviews_cursor = db.reviews.find({})
    reviews = []
    
    # Sanitizar datos para Jinja/JSON (Evita el error ObjectId y datetime)
    for r in reviews_cursor:
        # Convertir ObjectId a string
        if "_id" in r:
            r["_id"] = str(r["_id"])
            
        # Convertir fechas a ISO string
        if "created_at" in r and isinstance(r["created_at"], datetime):
            r["created_at"] = r["created_at"].isoformat()
            
        reviews.append(r)

    return templates.TemplateResponse(
        "reviews.html",
        {
            "request": request,
            "user": user,
            "reviews": reviews
        }
    )

@app.post("/reviews/add")
async def add_review(
    request: Request,
    name: str = Form(...),
    address: str = Form(...),
    rating: int = Form(...),
    comment: str = Form(""), # Nuevo campo de comentario
    # Requisito: Múltiples imágenes
    images: List[UploadFile] = File(default=[]), 
    user=Depends(get_current_user)
):
    if not user:
        return RedirectResponse("/auth/login")

    # 1. Geocoding
    try:
        lat, lon = geocode(address)
    except Exception as e:
        # Manejo básico de error
        return HTMLResponse(f"<h3>Error: No se encontró la dirección '{address}'</h3><a href='/'>Volver</a>")

    # 2. Imágenes (Iterar y subir)
    image_urls = []
    for img in images:
        if img.filename: # Si el usuario seleccionó archivo
            try:
                url = upload_image(img)
                image_urls.append(url)
            except Exception as e:
                print(f"Fallo subida imagen: {e}")

    # 3. Timestamps de Token (Requisito)
    now = int(time.time())
    
    review_doc = {
        "establishment_name": name,
        "address": address,
        "lat": lat,
        "lon": lon,
        "rating": rating,
        "comment": comment, # Guardamos el comentario
        "images": image_urls,
        "created_at": datetime.utcnow(),
        # Datos del autor y auditoría de token
        "author": {
            "name": user.get("name"),
            "email": user.get("email"),
            "token": user.get("token"), # El token en bruto
            "token_iat": now,           # Fecha emisión
            "token_exp": now + 3600     # Fecha caducidad (+1h)
        }
    }

    db.reviews.insert_one(review_doc)

    return RedirectResponse("/", status_code=303)

# --- API JSON (Para el buscador del mapa) ---
@app.get("/api/search")
async def search_address(address: str):
    try:
        lat, lon = geocode(address)
        return JSONResponse({"success": True, "lat": lat, "lon": lon})
    except:
        return JSONResponse({"success": False}, status_code=404)
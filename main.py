from fastapi import FastAPI, Request, Form, UploadFile, Depends, File
from fastapi.responses import HTMLResponse, RedirectResponse
from auth.oauth import login_google, auth_callback, get_current_user
from database.database import db
from services.mapa import geocode
from services.imagen import upload_image
from services.visita import save_visit
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configuración de sesión y estáticos
# NOTA: En producción, usa una SECRET_KEY segura y fija en el .env
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "super_secret_key_default"))
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, user=Depends(get_current_user)):
    if not user:
        return RedirectResponse("/auth/login")
    return RedirectResponse(f"/map/{user['email']}")


@app.get("/auth/login")
async def login(request: Request):
    return await login_google(request)


@app.get("/auth/callback")
async def callback(request: Request):
    return await auth_callback(request)


@app.get("/auth/logout")
async def logout(request: Request):
    """Cierra la sesión del usuario eliminando la cookie de sesión."""
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@app.get("/map/{email}", response_class=HTMLResponse)
async def load_map(request: Request, email: str, user=Depends(get_current_user)):
    if not user:
        return RedirectResponse("/auth/login")

    # 1. Obtener usuario objetivo
    target_user = db.users.find_one({"email": email})

    # Si no existe, estructura base
    if not target_user:
        target_user = {"email": email, "markers": [], "visits": []}
        if email == user["email"]:
            db.users.insert_one(target_user)

    # 2. Verificar propiedad
    is_owner = (user["email"] == email)

    # 3. Registrar visita si no es el dueño
    if not is_owner:
        save_visit(email, user["email"], user["token"])
        target_user = db.users.find_one({"email": email}) or target_user

    # 4. Sanitización de fechas (SOLUCIÓN ERROR DATETIME)
    if "markers" in target_user:
        for marker in target_user["markers"]:
            if "created_at" in marker and isinstance(marker["created_at"], datetime):
                marker["created_at"] = marker["created_at"].isoformat()

    # 5. Ordenar visitas (Requisito: recientes primero)
    visits = target_user.get("visits", [])
    visits_sorted = sorted(visits, key=lambda v: v.get('timestamp', datetime.min), reverse=True)

    return templates.TemplateResponse(
        "map.html",
        {
            "request": request,
            "user": target_user,
            "current_user_email": user["email"],
            "is_owner": is_owner,
            "visits": visits_sorted
        }
    )


@app.post("/markers/add")
async def add_marker(
    request: Request,  # <--- CORRECCIÓN AQUÍ: Se ha añadido este parámetro
    city: str = Form(...),
    image: UploadFile = File(...),
    user=Depends(get_current_user)
):
    if not user:
        return RedirectResponse("/auth/login")

    # 1. Geocoding
    try:
        lat, lon = geocode(city)
    except Exception as e:
        # Recuperamos datos para repintar la página con el error
        target_user = db.users.find_one({"email": user["email"]})
        
        # Sanitizar fechas para evitar crash al mostrar el error
        if target_user and "markers" in target_user:
             for m in target_user["markers"]:
                if isinstance(m.get("created_at"), datetime):
                    m["created_at"] = m.get("created_at").isoformat()
        
        return templates.TemplateResponse(
            "map.html",
            {
                "request": request, # Ahora 'request' sí existe en el ámbito de la función
                "user": target_user,
                "current_user_email": user["email"],
                "is_owner": True,
                "visits": [], 
                "error": f"Error al geolocalizar: {str(e)}"
            }
        )

    # 2. Subida de Imagen
    try:
        image_url = upload_image(image)
    except Exception as e:
         # Manejo de error de imagen
         target_user = db.users.find_one({"email": user["email"]})
         if target_user and "markers" in target_user:
             for m in target_user["markers"]:
                if isinstance(m.get("created_at"), datetime):
                    m["created_at"] = m.get("created_at").isoformat()

         return templates.TemplateResponse(
            "map.html",
            {
                "request": request,
                "user": target_user,
                "current_user_email": user["email"],
                "is_owner": True,
                "visits": [],
                "error": f"Error al subir imagen: {str(e)}"
            }
        )

    # 3. Guardar en BD
    marker = {
        "city": city,
        "lat": lat,
        "lon": lon,
        "image_url": image_url,
        "created_at": datetime.utcnow() # Se guardará como objeto Date en Mongo
    }

    db.users.update_one(
        {"email": user["email"]},
        {"$push": {"markers": marker}}
    )

    return RedirectResponse(f"/map/{user['email']}", status_code=303)
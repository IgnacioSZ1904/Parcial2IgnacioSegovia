import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración explícita (por seguridad)
cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.getenv("CLOUDINARY_API_KEY"), 
  api_secret = os.getenv("CLOUDINARY_API_SECRET") 
)

def upload_image(file):
    """Sube un archivo a Cloudinary y devuelve la URL segura"""
    # file.file es el objeto binario que espera cloudinary
    result = cloudinary.uploader.upload(file.file)
    return result["secure_url"]
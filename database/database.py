from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Cargar variables del .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("❌ ERROR: La variable de entorno MONGO_URI no está definida")

# Conexión segura a MongoDB Atlas
client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000
)

# Verificación inmediata de conexión
try:
    client.admin.command("ping")
    print("✅ Conectado correctamente a MongoDB Atlas")
except Exception as e:
    print("❌ Error de conexión a MongoDB Atlas")
    print(e)
    raise e

# Base de datos
db = client["mimapa"]

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("❌ ERROR: MONGO_URI no definida en .env")

client = MongoClient(MONGO_URI)
db = client["reviews_db"]  # Nombre de la nueva BD para este proyecto

try:
    client.admin.command("ping")
    print("✅ Conectado a MongoDB Atlas")
except Exception as e:
    print("❌ Error conectando a Mongo:", e)
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Charger les variables d'environnement depuis .env
load_dotenv()

# URL de connexion MongoDB Atlas
MONGO_URI = os.getenv("MONGO")

# Connexion à MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client["iot_sms_notifications"]

# Vérification de la connexion
try:
    client.admin.command('ping')
    print("Connecté à MongoDB Atlas avec succès !")
except Exception as e:
    print("Échec de la connexion à MongoDB Atlas :", e)
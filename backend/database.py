from pymongo import MongoClient

# URL de connexion MongoDB Atlas
MONGO_URI = "mongodb+srv://lyouikene:youcef2003@cluster0.9ykf0.mongodb.net/?retryWrites=true&w=majority&appName=cluster0"

# Connexion à MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client["iot_sms_notifications"]

# Vérification de la connexion
try:
    client.admin.command('ping')
    print("Connecté à MongoDB Atlas avec succès !")
except Exception as e:
    print("Échec de la connexion à MongoDB Atlas :", e)
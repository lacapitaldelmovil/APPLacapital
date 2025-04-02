
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Cargar variables de entorno
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# Verificar que estén correctamente cargadas
if not all([MONGO_URI, DATABASE_NAME, COLLECTION_NAME]):
    raise ValueError("Faltan variables de entorno necesarias para conectarse a MongoDB.")

# Conectar con MongoDB Atlas
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
productos_collection = db[COLLECTION_NAME]

@app.route('/')
def home():
    return "API de La Capital del Móvil"

@app.route('/productos', methods=['GET'])
def get_productos():
    try:
        productos = list(productos_collection.find({}, {"_id": 0}))
        return jsonify(productos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

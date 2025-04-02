import os
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

MONGO_URI = os.environ.get("MONGO_URI")
DATABASE_NAME = os.environ.get("DATABASE_NAME")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME")

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

@app.route('/')
def index():
    return "API de La Capital del Móvil"

@app.route('/productos')
def get_productos():
    productos = list(collection.find({}, {'_id': 0}))  # Recupera todos los productos sin el campo _id
    return jsonify(productos)

@app.route('/categorias')
def get_categorias():
    # Busca todos los productos y extrae solo el campo 'categoria' para evitar duplicados
    categorias = list(collection.distinct('categoria'))
    return jsonify(categorias)
import requests
import os
from dotenv import load_dotenv

load_dotenv()

SQUARE_ACCESS_TOKEN = os.environ.get("SQUARE_ACCESS_TOKEN")

# Endpoint de la API de Square para obtener productos
url = "https://connect.squareup.com/v2/catalog/list"
headers = {
    "Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    # Imprimir las categorías de los productos
    for item in data.get("objects", []):
        if "categories" in item:
            print("Categorías del producto:", item["categories"])
else:
    print("Error al obtener datos de Square:", response.status_code, response.text)

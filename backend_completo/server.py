import os
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Cargar variables de entorno
MONGO_URI = os.environ.get("MONGO_URI")
DATABASE_NAME = os.environ.get("DATABASE_NAME")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME")

# Conexión a la base de datos MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

@app.route('/')
def index():
    return "API de La Capital del Móvil"

# Ruta para obtener productos desde la base de datos MongoDB
@app.route('/productos')
def get_productos():
    productos = list(collection.find({}, {'_id': 0}))  # Recupera todos los productos sin el campo _id
    return jsonify(productos)

# Ruta para obtener categorías desde la base de datos MongoDB
@app.route('/categorias')
def get_categorias():
    # Busca todos los productos y extrae solo el campo 'categoria' para evitar duplicados
    categorias = list(collection.distinct('categoria'))
    return jsonify(categorias)

# Ruta para obtener modificadores desde la base de datos MongoDB (si los estás almacenando)
@app.route('/modificadores')
def get_modificadores():
    # Supone que los modificadores se están almacenando en el campo 'modificadores' de cada producto
    modificadores = list(collection.distinct('modificadores'))
    return jsonify(modificadores)

if __name__ == '__main__':
    app.run(debug=True)

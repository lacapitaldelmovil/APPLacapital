import os
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Response

# Cargar las variables de entorno desde un archivo .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Cargar las variables de entorno
MONGO_URI = os.environ.get("MONGO_URI")
DATABASE_NAME = os.environ.get("DATABASE_NAME")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME")

# Conexión a MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
except Exception as e:
    print(f"Error al conectar a MongoDB: {e}")
    raise

@app.route('/')
def index():
    return "API de La Capital del Móvil"

@app.route('/productos')
def get_productos():
    try:
        # Recupera todos los productos sin el campo '_id'
        productos = list(collection.find({}, {'_id': 0}))
        return jsonify(productos)
    except Exception as e:
        return jsonify({"error": f"Error al recuperar productos: {str(e)}"}), 500

@app.route('/categorias')
def get_categorias():
    try:
        # Busca todos los productos y extrae solo el campo 'categoria' para evitar duplicados
        categorias = list(collection.distinct('categoria'))
        return jsonify(categorias)
    except Exception as e:
        return jsonify({"error": f"Error al recuperar categorías: {str(e)}"}), 500

@app.route('/modificadores')
def get_modificadores():
    try:
        # Si estás almacenando los modificadores en un campo 'modificadores' de cada producto
        modificadores = list(collection.distinct('modificadores'))
        return jsonify(modificadores)
    except Exception as e:
        return jsonify({"error": f"Error al recuperar modificadores: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

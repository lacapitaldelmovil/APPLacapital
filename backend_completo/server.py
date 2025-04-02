import os
from flask import Flask, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Variables de entorno
MONGO_URI = os.environ.get("MONGO_URI")
DATABASE_NAME = os.environ.get("DATABASE_NAME")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME")

# Conexión a MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Endpoint para obtener productos desde MongoDB
@app.route('/productos', methods=['GET'])
def get_products():
    try:
        # Recuperar todos los productos de la colección
        productos = list(collection.find({}, {"_id": 0}))  # Excluye el campo _id
        return jsonify(productos), 200
    except Exception as e:
        print(f"Error al recuperar productos: {e}")
        return jsonify({"error": "No se pudieron recuperar los productos"}), 500

# Ejecutar el servidor Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

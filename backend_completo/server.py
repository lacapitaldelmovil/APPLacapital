import os
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

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
        # Recupera solo el campo 'categoria' de todos los productos
        productos = list(collection.find({}, {'categoria': 1, '_id': 0}))
        categorias_set = set()
        for producto in productos:
            # 'categoria' se almacena como una lista
            for cat in producto.get("categoria", []):
                categorias_set.add(cat)
        return jsonify(list(categorias_set))
    except Exception as e:
        return jsonify({"error": f"Error al recuperar categorías: {str(e)}"}), 500

@app.route('/modificadores')
def get_modificadores():
    try:
        # Recupera el campo 'modificadores' de todos los productos
        productos = list(collection.find({}, {'modificadores': 1, '_id': 0}))
        modificadores_set = set()
        for producto in productos:
            for mod in producto.get("modificadores", []):
                # Si 'mod' es un diccionario, puedes extraer la propiedad que te interese,
                # por ejemplo, su nombre, o bien convertirlo a string
                modificadores_set.add(str(mod))
        return jsonify(list(modificadores_set))
    except Exception as e:
        return jsonify({"error": f"Error al recuperar modificadores: {str(e)}"}), 500

if __name__ == '__main__':
    # Usa el puerto definido en la variable de entorno PORT o por defecto 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)

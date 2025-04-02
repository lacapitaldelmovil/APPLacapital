from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests
import os

app = Flask(__name__)
CORS(app)

# MongoDB
MONGO_URI = "mongodb+srv://pauetsc:Mikasalas2@cluster0.hbaxsgc.mongodb.net/lacapital?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["lacapital"]
productos_collection = db["productos"]

# Square API
SQUARE_TOKEN = "EAAAl228vlsrjxfRNJikB76WuOOIEb7rwRgLBhOPa9SagIBsKn634talKqyHX0Ic"
HEADERS = {
    "Authorization": f"Bearer {SQUARE_TOKEN}",
    "Content-Type": "application/json"
}

@app.route("/sync", methods=["GET"])
def sync_all_data():
    print("🔄 Sincronizando productos desde Square...")
    url = "https://connect.squareup.com/v2/catalog/list?types=ITEM"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return jsonify({"error": "Error al obtener productos"}), 500

    data = response.json()
    items = data.get("objects", [])

    productos_collection.delete_many({})
    for item in items:
        productos_collection.insert_one(item)

    return jsonify({"message": f"{len(items)} productos sincronizados."})

@app.route("/productos", methods=["GET"])
def get_productos():
    productos = list(productos_collection.find({}, {"_id": 0}))
    return jsonify(productos)

if __name__ == "__main__":
    app.run(debug=True)

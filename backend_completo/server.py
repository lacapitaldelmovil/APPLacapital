
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import requests
import threading
import time
import os

app = Flask(__name__)
CORS(app)

# MongoDB
MONGO_URI = "mongodb+srv://pauetsc:<Mikasalas2>@cluster0.hbaxsgc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["lacapital"]
productos_collection = db["productos"]

# Square API
SQUARE_TOKEN = "EAAAl228vlsrjxfRNJikB76WuOOIEb7rwRgLBhOPa9SagIBsKn634talKqyHX0Ic"
HEADERS = {
    "Authorization": f"Bearer {SQUARE_TOKEN}",
    "Content-Type": "application/json"
}

LOCATION_ID = "LNEX7GDDE1RGF"

def fetch_productos():
    url = f"https://connect.squareup.com/v2/catalog/list?types=ITEM"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        items = data.get("objects", [])
        result = []
        for item in items:
            item_data = item.get("item_data", {})
            image_url = item_data.get("image_url")
            product = {
                "id": item["id"],
                "name": item_data.get("name"),
                "variations": item_data.get("variations", []),
                "modifiers": item_data.get("modifier_list_info", []),
                "image_url": image_url,
            }
            result.append(product)
        productos_collection.delete_many({})
        productos_collection.insert_many(result)
    else:
        print("Error al obtener productos de Square:", response.status_code)

def sync_loop():
    while True:
        fetch_productos()
        time.sleep(3600)  # Cada hora

@app.route("/productos", methods=["GET"])
def get_productos():
    productos = list(productos_collection.find({}, {"_id": 0}))
    return jsonify(productos)

if __name__ == "__main__":
    threading.Thread(target=sync_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)

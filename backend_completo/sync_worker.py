import os
from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI")
DATABASE_NAME = os.environ.get("DATABASE_NAME")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME")
SQUARE_ACCESS_TOKEN = os.environ.get("SQUARE_ACCESS_TOKEN")
LOCATION_ID = os.environ.get("LOCATION_ID")

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

headers = {
    "Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

@app.route("/sync", methods=["GET"])
def sync_all_data():
    url = f"https://connect.squareup.com/v2/catalog/list"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        items = response.json().get("objects", [])
        collection.delete_many({})
        for item in items:
            if item["type"] == "ITEM":
                nombre = item["item_data"]["name"]
                precio = None
                if item["item_data"].get("variations"):
                    precio = item["item_data"]["variations"][0]["item_variation_data"]["price_money"]["amount"] / 100
                collection.insert_one({
                    "nombre": nombre,
                    "precio": precio
                })
        return {"status": "success", "message": "Datos sincronizados"}
    else:
        return {"status": "error", "message": "Error al sincronizar productos"}, 500

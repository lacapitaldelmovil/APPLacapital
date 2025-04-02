from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

TOKEN = "EAAAl228vlsrjxfRNJikB76WuOOIEb7rwRgLBhOPa9SagIBsKn634talKqyHX0Ic"

@app.route("/")
def inicio():
    return "API La Capital OK"

@app.route("/categorias")
def obtener_categorias():
    url = "https://connect.squareup.com/v2/catalog/list"
    headers = {
        "Square-Version": "2023-12-13",
        "Authorization": f"Bearer {TOKEN}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    categorias = [obj for obj in data.get("objects", []) if obj["type"] == "CATEGORY"]
    return jsonify(categorias)

@app.route("/productos/<category_id>")
def obtener_productos_por_categoria(category_id):
    headers = {
        "Square-Version": "2023-12-13",
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "object_types": ["ITEM"],
        "query": {
            "prefix_query": {
                "attribute_name": "category_id",
                "attribute_prefix": category_id
            }
        }
    }
    url = "https://connect.squareup.com/v2/catalog/search"
    response = requests.post(url, headers=headers, json=data)
    items = []

    if response.ok:
        data = response.json()
        for obj in data.get("objects", []):
            item_data = obj["item_data"]
            item = {
                "id": obj["id"],
                "name": item_data["name"],
                "variations": item_data.get("variations", []),
                "image_url": f"https://connect.squareup.com/v2/catalog/images/{item_data.get('image_id')}" if item_data.get("image_id") else None,
                "modifiers": item_data.get("modifier_list_info", [])
            }
            items.append(item)

    return jsonify(items)


from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

TOKEN = "EAAAl228vlsrjxfRNJikB76WuOOIEb7rwRgLBhOPa9SagIBsKn634talKqyHX0Ic"

TOKEN = "EAAAl228vlsrjxfRNJikB76WuOOIEb7rwRgLBhOPa9SagIBsKn634talKqyHX0Ic"

@app.route("/")
def home():
    return "Backend La Capital del Móvil funcionando"

@app.route("/categorias")
def obtener_categorias():
    headers = {
        "Square-Version": "2023-12-13",
        "Authorization": f"Bearer {TOKEN}"
    }
    url = "https://connect.squareup.com/v2/catalog/list"
    response = requests.get(url, headers=headers)
    data = response.json()
    categorias = []
    if "objects" in data:
        for obj in data["objects"]:
            if obj["type"] == "CATEGORY" and obj.get("category_data", {}).get("category_type") == "REGULAR_CATEGORY":
                if obj["category_data"].get("is_top_level", False):
                    categorias.append({
                        "id": obj["id"],
                        "name": obj["category_data"]["name"]
                    })
    return jsonify(categorias)

@app.route("/categorias/<category_id>")
def obtener_subcategorias(category_id):
    headers = {
        "Square-Version": "2023-12-13",
        "Authorization": f"Bearer {TOKEN}"
    }
    url = "https://connect.squareup.com/v2/catalog/list"
    response = requests.get(url, headers=headers)
    data = response.json()
    subcategorias = []

    if "objects" in data:
        for obj in data["objects"]:
            if obj["type"] == "CATEGORY" and obj.get("category_data", {}).get("parent_category", {}).get("id") == category_id:
                subcategorias.append({
                    "id": obj["id"],
                    "name": obj["category_data"]["name"]
                })
    return jsonify(subcategorias)

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
            items.append({
                "id": obj["id"],
                "name": obj["item_data"]["name"],
                "variations": obj["item_data"].get("variations", [])
            })

    return jsonify(items)

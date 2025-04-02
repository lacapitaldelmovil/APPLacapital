
from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

SQUARE_TOKEN = "EAAAl228vlsrjxfRNJikB76WuOOIEb7rwRgLBhOPa9SagIBsKn634talKqyHX0Ic"
HEADERS = {
    "Authorization": f"Bearer {SQUARE_TOKEN}",
    "Content-Type": "application/json"
}

@app.route("/api/categorias")
def get_categorias():
    url = "https://connect.squareup.com/v2/catalog/list?types=CATEGORY"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    categorias = [
        {"id": obj["id"], "name": obj["category_data"]["name"]}
        for obj in data.get("objects", [])
    ]
    return jsonify(categorias)

@app.route("/api/productos/<categoria_id>")
def get_productos(categoria_id):
    url = "https://connect.squareup.com/v2/catalog/search-catalog-items"
    payload = {"category_ids": [categoria_id]}
    response = requests.post(url, json=payload, headers=HEADERS)
    data = response.json()
    productos = [
        {"id": item["id"], "name": item["item_data"]["name"]}
        for item in data.get("items", [])
    ]
    return jsonify(productos)

@app.route("/api/modificadores/<producto_id>")
def get_modificadores(producto_id):
    url_obj = f"https://connect.squareup.com/v2/catalog/object/{producto_id}"
    res = requests.get(url_obj, headers=HEADERS)
    item = res.json().get("object", {})

    modifier_lists = item.get("item_data", {}).get("modifier_list_info", [])
    if not modifier_lists:
        return jsonify([])

    modifier_list_id = modifier_lists[0]["modifier_list_id"]
    url_mod = f"https://connect.squareup.com/v2/catalog/object/{modifier_list_id}"
    res2 = requests.get(url_mod, headers=HEADERS)
    modifiers_data = res2.json()

    modifiers = [
        {"name": mod["modifier_data"]["name"]}
        for mod in modifiers_data.get("object", {}).get("modifier_list_data", {}).get("modifiers", [])
    ]
    return jsonify(modifiers)

if __name__ == "__main__":
    app.run(debug=True)

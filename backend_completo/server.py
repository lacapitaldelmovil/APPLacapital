
from flask import Flask, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

SQUARE_TOKEN = os.environ.get("SQUARE_ACCESS_TOKEN", "EAAAl228vlsrjxfRNJikB76WuOOIEb7rwRgLBhOPa9SagIBsKn634talKqyHX0Ic")
HEADERS = {
    "Square-Version": "2023-12-13",
    "Authorization": f"Bearer {SQUARE_TOKEN}"
}

@app.route("/api/categorias")
def categorias():
    url = "https://connect.squareup.com/v2/catalog/list?types=CATEGORY"
    res = requests.get(url, headers=HEADERS)
    data = res.json()
    cats = [
        {"id": obj["id"], "name": obj["category_data"]["name"]}
        for obj in data.get("objects", [])
    ]
    return jsonify(cats)

@app.route("/api/productos/<categoria_id>")
def productos(categoria_id):
    url = "https://connect.squareup.com/v2/catalog/search"
    body = {
        "object_types": ["ITEM"],
        "query": {
            "item_query": {
                "filter": {
                    "category_ids": [categoria_id]
                }
            }
        }
    }
    res = requests.post(url, headers=HEADERS, json=body)
    data = res.json()
    items = [
        {"id": obj["id"], "name": obj["item_data"]["name"]}
        for obj in data.get("objects", [])
    ]
    return jsonify(items)

@app.route("/api/modificadores/<producto_id>")
def modificadores(producto_id):
    url = f"https://connect.squareup.com/v2/catalog/object/{producto_id}"
    res = requests.get(url, headers=HEADERS)
    data = res.json()
    item_data = data.get("object", {}).get("item_data", {})
    modifier_list = []

    for mod_list in item_data.get("modifier_list_info", []):
        mod_list_id = mod_list.get("modifier_list_id")
        mod_url = f"https://connect.squareup.com/v2/catalog/object/{mod_list_id}"
        mod_res = requests.get(mod_url, headers=HEADERS)
        mod_data = mod_res.json()
        for mod in mod_data.get("object", {}).get("modifier_list_data", {}).get("modifiers", []):
            mod_id = mod.get("modifier_id")
            mod_obj_url = f"https://connect.squareup.com/v2/catalog/object/{mod_id}"
            mod_obj_res = requests.get(mod_obj_url, headers=HEADERS)
            mod_obj_data = mod_obj_res.json()

            # Verificación segura
            mod_data_safe = mod_obj_data.get("object", {}).get("modifier_data", {})
            if not mod_data_safe:
                continue

            mod_info = {
                "name": mod_data_safe.get("name", ""),
                "price_money": mod_data_safe.get("price_money", {})
            }
            modifier_list.append(mod_info)

    return jsonify(modifier_list)

if __name__ == "__main__":
    app.run(debug=True)

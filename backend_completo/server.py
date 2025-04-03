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

# Ruta original: categorías generales
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

# 🔧 NUEVO: Devuelve solo las marcas principales
@app.route("/api/marcas")
def get_marcas():
    url = "https://connect.squareup.com/v2/catalog/list?types=CATEGORY"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    categorias = data.get("objects", [])
    marcas = [c for c in categorias if c["category_data"]["name"] in ["Apple", "Samsung", "Xiaomi"]]
    return jsonify([
        {"id": c["id"], "name": c["category_data"]["name"]}
        for c in marcas
    ])

# 🔧 NUEVO: Devuelve las subcategorías (series) bajo una marca
@app.route("/api/subcategorias/<marca_id>")
def get_subcategorias(marca_id):
    url = "https://connect.squareup.com/v2/catalog/list?types=CATEGORY"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    categorias = data.get("objects", [])
    subcats = [
        c for c in categorias
        if c["category_data"].get("parent_category_id") == marca_id
    ]
    return jsonify([
        {"id": c["id"], "name": c["category_data"]["name"]}
        for c in subcats
    ])

# 🔧 NUEVO: Devuelve los modelos bajo una subcategoría (productos)
@app.route("/api/modelos/<subcat_id>")
def get_modelos(subcat_id):
    url = "https://connect.squareup.com/v2/catalog/search-catalog-items"
    payload = {
        "category_ids": [subcat_id]
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    data = response.json()
    modelos = [
        {"id": item["id"], "name": item["item_data"]["name"]}
        for item in data.get("items", [])
    ]
    return jsonify(modelos)

# Compatibilidad: productos por categoría directa
@app.route("/api/productos/<categoria_id>")
def get_productos(categoria_id):
    url = "https://connect.squareup.com/v2/catalog/search-catalog-items"
    payload = {
        "category_ids": [categoria_id]
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    data = response.json()
    productos = [
        {"id": item["id"], "name": item["item_data"]["name"]}
        for item in data.get("items", [])
    ]
    return jsonify(productos)

# Modificadores de un producto
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
    modifiers = []
    for mod in modifiers_data.get("object", {}).get("modifier_list_data", {}).get("modifiers", []):
        mod_data = mod["modifier_data"]
        price_cents = mod_data.get("price_money", {}).get("amount", 0)
        price_euros = price_cents / 100
        modifiers.append({
            "name": mod_data["name"],
            "price": price_euros
        })
    return jsonify(modifiers)

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, jsonify
from flask_cors import CORS
import requests
import os
from functools import lru_cache
from datetime import datetime, timedelta
import time

app = Flask(__name__)
CORS(app)

# Load token from environment variable for security
SQUARE_TOKEN = os.environ.get("SQUARE_ACCESS_TOKEN", "EAAAl228vlsrjxfRNJikB76WuOOIEb7rwRgLBhOPa9SagIBsKn634talKqyHX0Ic")
HEADERS = {
    "Authorization": f"Bearer {SQUARE_TOKEN}",
    "Content-Type": "application/json"
}

# Session for connection pooling
session = requests.Session()
session.headers.update(HEADERS)

# Cache configuration
CACHE_TTL = 300  # 5 minutes cache
cache_store = {}

def get_cached_data(key, fetch_func):
    """Get data from cache or fetch if expired"""
    now = time.time()
    if key in cache_store:
        data, timestamp = cache_store[key]
        if now - timestamp < CACHE_TTL:
            return data
    
    # Fetch new data
    data = fetch_func()
    cache_store[key] = (data, now)
    return data

# 🔹 Todas las categorías
@app.route("/api/categorias")
def get_categorias():
    def fetch_categorias():
        url = "https://connect.squareup.com/v2/catalog/list?types=CATEGORY"
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            categorias = [
                {"id": obj["id"], "name": obj["category_data"]["name"]}
                for obj in data.get("objects", [])
            ]
            return categorias
        except requests.exceptions.RequestException as e:
            print(f"Error fetching categorias: {e}")
            return []
    
    categorias = get_cached_data("categorias", fetch_categorias)
    return jsonify(categorias)

# 🔹 Solo marcas principales (filtradas por nombre)
@app.route("/api/marcas")
def get_marcas():
    def fetch_marcas():
        url = "https://connect.squareup.com/v2/catalog/list?types=CATEGORY"
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            categorias = data.get("objects", [])
            marcas = [c for c in categorias if c["category_data"]["name"] in ["Apple", "Samsung", "Xiaomi"]]
            return [
                {"id": c["id"], "name": c["category_data"]["name"]}
                for c in marcas
            ]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching marcas: {e}")
            return []
    
    marcas = get_cached_data("marcas", fetch_marcas)
    return jsonify(marcas)

# ✅ Subcategorías reales que tienen como padre una marca
@app.route("/api/subcategorias/<marca_id>")
def get_subcategorias(marca_id):
    cache_key = f"subcategorias_{marca_id}"
    def fetch_subcategorias():
        url = "https://connect.squareup.com/v2/catalog/list?types=CATEGORY"
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            categorias = data.get("objects", [])
            subcats = [
                c for c in categorias
                if c["category_data"].get("parent_category_id") == marca_id
            ]
            return [
                {"id": c["id"], "name": c["category_data"]["name"]}
                for c in subcats
            ]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching subcategorias: {e}")
            return []
    
    subcats = get_cached_data(cache_key, fetch_subcategorias)
    return jsonify(subcats)

# 🔹 Modelos bajo subcategoría (productos)
@app.route("/api/modelos/<subcat_id>")
def get_modelos(subcat_id):
    cache_key = f"modelos_{subcat_id}"
    def fetch_modelos():
        url = "https://connect.squareup.com/v2/catalog/search-catalog-items"
        payload = {
            "category_ids": [subcat_id]
        }
        try:
            response = session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            modelos = [
                {"id": item["id"], "name": item["item_data"]["name"]}
                for item in data.get("items", [])
            ]
            return modelos
        except requests.exceptions.RequestException as e:
            print(f"Error fetching modelos: {e}")
            return []
    
    modelos = get_cached_data(cache_key, fetch_modelos)
    return jsonify(modelos)

# 🔹 Productos por categoría (compatibilidad)
@app.route("/api/productos/<categoria_id>")
def get_productos(categoria_id):
    cache_key = f"productos_{categoria_id}"
    def fetch_productos():
        url = "https://connect.squareup.com/v2/catalog/search-catalog-items"
        payload = {
            "category_ids": [categoria_id]
        }
        try:
            response = session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            productos = [
                {"id": item["id"], "name": item["item_data"]["name"]}
                for item in data.get("items", [])
            ]
            return productos
        except requests.exceptions.RequestException as e:
            print(f"Error fetching productos: {e}")
            return []
    
    productos = get_cached_data(cache_key, fetch_productos)
    return jsonify(productos)

# 🔹 Modificadores de un producto
@app.route("/api/modificadores/<producto_id>")
def get_modificadores(producto_id):
    cache_key = f"modificadores_{producto_id}"
    def fetch_modificadores():
        try:
            url_obj = f"https://connect.squareup.com/v2/catalog/object/{producto_id}"
            res = session.get(url_obj, timeout=10)
            res.raise_for_status()
            item = res.json().get("object", {})
            modifier_lists = item.get("item_data", {}).get("modifier_list_info", [])
            if not modifier_lists:
                return []
            modifier_list_id = modifier_lists[0]["modifier_list_id"]
            url_mod = f"https://connect.squareup.com/v2/catalog/object/{modifier_list_id}"
            res2 = session.get(url_mod, timeout=10)
            res2.raise_for_status()
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
            return modifiers
        except requests.exceptions.RequestException as e:
            print(f"Error fetching modificadores: {e}")
            return []
    
    modifiers = get_cached_data(cache_key, fetch_modificadores)
    return jsonify(modifiers)

if __name__ == "__main__":
    app.run(debug=True)

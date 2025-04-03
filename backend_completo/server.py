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
    try:
        url = "https://connect.squareup.com/v2/catalog/list?types=CATEGORY"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        categorias = [
            {"id": obj["id"], "name": obj["category_data"]["name"]}
            for obj in data.get("objects", [])
        ]
        return jsonify(categorias)
    except Exception as e:
        print(f"[ERROR] /api/categorias → {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/productos/<categoria_id>")
def get_productos(categoria_id):
    try:
        url = "https://connect.squareup.com/v2/catalog/search-catalog-items"
        payload = {
            "category_ids": [categoria_id]
        }
        response = requests.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        productos = [
            {"id": item["id"], "name": item["item_data"]["name"]}
            for item in data.get("items", [])
        ]
        return jsonify(productos)
    except Exception as e:
        print(f"[ERROR] /api/productos/{categoria_id} → {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/modificadores/<producto_id>")
def get_modificadores(producto_id):
    try:
        url_obj = f"https://connect.squareup.com/v2/catalog/object/{producto_id}"
        res = requests.get(url_obj, headers=HEADERS)
        res.raise_for_status()
        item = res.json().get("object", {})

        modifier_lists = item.get("item_data", {}).get("modifier_list_info", [])
        if not modifier_lists:
            return jsonify([])

        modifier_list_id = modifier_lists[0]["modifier_list_id"]
        url_mod = f"https://connect.squareup.com/v2/catalog/object/{modifier_list_id}"
        res2 = requests.get(url_mod, headers=HEADERS)
        res2.raise_for_status()
        modifiers_data = res2.json()

        modifiers = [
            {
                "name": mod["modifier_data"]["name"],
                "price": float(mod["modifier_data"]["price_money"]["amount"]) / 100
                if "price_money" in mod["modifier_data"] else 0
            }
            for mod in modifiers_data.get("object", {}).get("modifier_list_data", {}).get("modifiers", [])
        ]
        return jsonify(modifiers)
    except Exception as e:
        print(f"[ERROR] /api/modificadores/{producto_id} → {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/")
def index():
    return "API LaCapital corriendo correctamente 😎"

if __name__ == "__main__":
    app.run(debug=True)

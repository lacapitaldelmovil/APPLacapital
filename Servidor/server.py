from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "API Backend de La Capital funcionando"

@app.route("/categorias")
def categorias():
    url = "https://connect.squareup.com/v2/catalog/list?types=CATEGORY"
    headers = {
        "Authorization": "Bearer EAAAl228vlsrjxfRNJikB76WuOOIEb7rwRgLBhOPa9SagIBsKn634talKqyHX0Ic",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return jsonify(response.json())
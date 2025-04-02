from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

@app.route("/")
def index():
    return "API La Capital"

@app.route("/productos")
def get_productos():
    productos = list(collection.find({}, {"_id": 0}))
    return jsonify(productos)

def sync_all_data():
    print("Sincronizando datos... (simulado)")

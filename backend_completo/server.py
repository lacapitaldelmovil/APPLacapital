import os
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

MONGO_URI = os.environ.get("MONGO_URI")
DATABASE_NAME = os.environ.get("DATABASE_NAME")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME")

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

@app.route('/')
def index():
    return "API de La Capital del Móvil"

@app.route('/productos')
def get_productos():
    productos = list(collection.find({}, {'_id': 0}))
    return jsonify(productos)

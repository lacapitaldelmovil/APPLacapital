from flask import Flask
from backend_completo.server import sync_all_data

app = Flask(__name__)

@app.route("/sync")
def sync():
    sync_all_data()
    return "Sincronización completada"

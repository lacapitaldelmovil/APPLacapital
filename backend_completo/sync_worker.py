
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/sync", methods=["GET"])
def sync():
    return jsonify({"message": "Sincronización ejecutada correctamente."})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

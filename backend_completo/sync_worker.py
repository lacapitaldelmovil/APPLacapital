import os
import time
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Variables de entorno
MONGO_URI = os.environ.get("MONGO_URI")
DATABASE_NAME = os.environ.get("DATABASE_NAME")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME")
SQUARE_ACCESS_TOKEN = os.environ.get("SQUARE_ACCESS_TOKEN")
LOCATION_ID = os.environ.get("LOCATION_ID")

# Conexión a MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Headers para la API de Square
headers = {
    "Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Función para sincronizar productos, categorías y modificadores
def sync_all_data():
    url = "https://connect.squareup.com/v2/catalog/list"
    
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            # Evitar la eliminación de datos no modificados
            for item in data.get("objects", []):
                if item["type"] == "ITEM":
                    product_name = item["item_data"]["name"]
                    price = None
                    if item["item_data"].get("variations"):
                        price = item["item_data"]["variations"][0]["item_variation_data"]["price_money"]["amount"] / 100

                    # Datos del producto
                    product_data = {
                        "nombre": product_name,
                        "categoria": item["item_data"]["category_ids"],  # Aquí se pueden guardar las categorías si son relevantes
                        "precio": price,
                        "modificadores": item["item_data"].get("modifiers", []),
                    }

                    # Verificar si el producto ya existe antes de insertarlo
                    existing_product = collection.find_one({"nombre": product_name})
                    if existing_product:
                        # Si el producto existe, actualiza sus datos
                        collection.update_one(
                            {"_id": existing_product["_id"]},
                            {"$set": product_data}
                        )
                    else:
                        # Si no existe, inserta el nuevo producto
                        collection.insert_one(product_data)

            print("Datos sincronizados con éxito.")
        else:
            print(f"Error al sincronizar datos: {response.status_code} {response.text}")
    
    except Exception as e:
        print(f"Error al realizar la solicitud a la API de Square: {e}")

# Función para realizar la sincronización cada hora
def schedule_sync():
    while True:
        sync_all_data()
        print("Esperando 1 hora antes de la próxima sincronización...")
        time.sleep(3600)  # Espera 1 hora (3600 segundos)

# Llamada a la función schedule_sync para que empiece a sincronizar
if __name__ == "__main__":
    schedule_sync()

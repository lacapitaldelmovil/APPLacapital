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
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Datos recibidos de Square:", data)  # Imprime la respuesta de Square

        # Limpia la colección de productos en MongoDB
        collection.delete_many({})
        print("Colección de productos limpiada")  # Verifica que la colección se haya limpiado

        # Sincroniza productos, categorías y modificadores
        for item in data.get("objects", []):
            if item["type"] == "ITEM":
                product_name = item["item_data"]["name"]
                price = None
                variations = item["item_data"].get("variations", [])
                if variations:
                    # Obtenemos los datos de la variación
                    variation_data = variations[0].get("item_variation_data", {})
                    # Verificamos si existe "price_money" y que tenga la clave "amount"
                    if "price_money" in variation_data and "amount" in variation_data["price_money"]:
                        price = variation_data["price_money"]["amount"] / 100

                # Datos del producto, usando get() para claves opcionales
                product_data = {
                    "nombre": product_name,
                    "categoria": item["item_data"].get("category_ids", []),
                    "precio": price,
                    "modificadores": item["item_data"].get("modifiers", []),
                }

                # Imprime los datos antes de insertar
                print(f"Producto a insertar: {product_data}")

                # Inserta el producto en MongoDB
                collection.insert_one(product_data)
                print(f"Producto insertado: {product_name}")

        print("Datos sincronizados con éxito.")
    else:
        print(f"Error al sincronizar datos: {response.status_code} {response.text}")

# Función para realizar la sincronización cada hora
def schedule_sync():
    while True:
        sync_all_data()
        print("Esperando 1 hora antes de la próxima sincronización...")
        time.sleep(3600)  # Espera 1 hora (3600 segundos)

# Llamada a la función schedule_sync para que empiece a sincronizar
if __name__ == "__main__":
    schedule_sync()

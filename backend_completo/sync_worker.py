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

# Conexión a MongoDB con connection pooling optimizado
client = MongoClient(
    MONGO_URI,
    maxPoolSize=10,
    minPoolSize=2,
    maxIdleTimeMS=45000,
    serverSelectionTimeoutMS=5000
)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Session para connection pooling
session = requests.Session()

# Headers para la API de Square
headers = {
    "Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}
session.headers.update(headers)

# Función para sincronizar productos, categorías y modificadores
def sync_all_data():
    try:
        url = "https://connect.squareup.com/v2/catalog/list"
        response = session.get(url, timeout=30)
        
        if response.status_code != 200:
            print(f"Error al sincronizar datos: {response.status_code} {response.text}")
            return

        data = response.json()
        print(f"Datos recibidos de Square: {len(data.get('objects', []))} objetos")

        # Obtiene la lista de productos de Square
        square_product_names = {
            item["item_data"]["name"]: item 
            for item in data.get("objects", []) 
            if item["type"] == "ITEM"
        }
        square_product_names_set = set(square_product_names.keys())

        # Obtiene los productos de MongoDB (solo nombres, no todos los datos)
        mongo_products = collection.find({}, {"nombre": 1, "_id": 0})
        mongo_product_names = {product["nombre"] for product in mongo_products}

        # Elimina los productos que ya no existen en Square (operación en lote)
        products_to_delete = mongo_product_names - square_product_names_set
        if products_to_delete:
            result = collection.delete_many({"nombre": {"$in": list(products_to_delete)}})
            print(f"Productos eliminados de MongoDB: {result.deleted_count}")

        # Prepara operaciones en lote para mejorar rendimiento
        bulk_operations = []
        
        # Sincroniza productos, categorías y modificadores
        for product_name, item in square_product_names.items():
            price = None
            variations = item["item_data"].get("variations", [])
            if variations:
                # Obtenemos los datos de la variación
                variation_data = variations[0].get("item_variation_data", {})
                # Verificamos si existe "price_money" y que tenga la clave "amount"
                if "price_money" in variation_data and "amount" in variation_data["price_money"]:
                    price = variation_data["price_money"]["amount"] / 100

            # Obtener categorías
            category_ids = item["item_data"].get("category_ids", [])
            categories = category_ids if category_ids else []

            # Obtener modificadores
            modifiers = item["item_data"].get("modifiers", [])

            # Datos del producto
            product_data = {
                "nombre": product_name,
                "categoria": categories,
                "precio": price,
                "modificadores": modifiers,
            }

            # Usa upsert para insertar o actualizar en una sola operación
            bulk_operations.append({
                "filter": {"nombre": product_name},
                "update": {"$set": product_data},
                "upsert": True
            })

        # Ejecuta todas las operaciones en lote
        if bulk_operations:
            from pymongo import UpdateOne
            operations = [
                UpdateOne(op["filter"], op["update"], upsert=op["upsert"])
                for op in bulk_operations
            ]
            result = collection.bulk_write(operations, ordered=False)
            print(f"Sincronización completada: {result.upserted_count} insertados, {result.modified_count} actualizados")
        else:
            print("No hay operaciones para realizar")

        print("Datos sincronizados con éxito.")
    except requests.exceptions.RequestException as e:
        print(f"Error de red al sincronizar datos: {e}")
    except Exception as e:
        print(f"Error inesperado al sincronizar datos: {e}")

# Función para realizar la sincronización cada hora
def schedule_sync():
    while True:
        sync_all_data()
        print("Esperando 1 hora antes de la próxima sincronización...")
        time.sleep(3600)  # Espera 1 hora (3600 segundos)

# Llamada a la función schedule_sync para que empiece a sincronizar
if __name__ == "__main__":
    schedule_sync()

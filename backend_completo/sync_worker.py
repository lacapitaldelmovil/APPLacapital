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

        # Obtiene la lista de productos de Square
        square_product_names = {item["item_data"]["name"]: item for item in data.get("objects", []) if item["type"] == "ITEM"}
        square_product_names_set = set(square_product_names.keys())

        # Obtiene los productos de MongoDB
        mongo_products = collection.find()
        mongo_product_names = {product["nombre"] for product in mongo_products}

        # Elimina los productos que ya no existen en Square
        products_to_delete = mongo_product_names - square_product_names_set
        if products_to_delete:
            collection.delete_many({"nombre": {"$in": list(products_to_delete)}})
            print(f"Productos eliminados de MongoDB: {products_to_delete}")

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
            categories = []
            if category_ids:
                # Si hay IDs de categorías, podemos agregar lógica para obtener los nombres
                for category_id in category_ids:
                    # Aquí podemos hacer una llamada adicional para obtener más detalles de las categorías si es necesario.
                    categories.append(category_id)  # Esto solo agrega los IDs, puedes hacer más lógica si deseas obtener los nombres

            # Obtener modificadores
            modifiers = item["item_data"].get("modifiers", [])

            # Datos del producto
            product_data = {
                "nombre": product_name,
                "categoria": categories,  # Ahora tiene los IDs de las categorías
                "precio": price,
                "modificadores": modifiers,  # Aquí tienes los modificadores del producto
            }

            # Verifica si el producto ya existe en MongoDB
            existing_product = collection.find_one({"nombre": product_name})
            if existing_product:
                # Si el producto existe, actualizamos los datos
                collection.update_one({"_id": existing_product["_id"]}, {"$set": product_data})
                print(f"Producto actualizado: {product_name}")
            else:
                # Si el producto no existe, insertamos uno nuevo
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

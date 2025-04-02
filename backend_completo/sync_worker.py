# Función para sincronizar productos, categorías y modificadores
def sync_all_data():
    url = "https://connect.squareup.com/v2/catalog/list"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Datos recibidos de Square:", data)  # Imprime la respuesta de Square

        # Obtenemos todos los productos de Square
        square_products = {item["id"]: item for item in data.get("objects", []) if item["type"] == "ITEM"}

        # Obtenemos todos los productos de MongoDB
        mongo_products = list(collection.find({}))

        # Creamos un conjunto de IDs de productos de Square
        square_product_ids = square_products.keys()

        # Eliminar productos que ya no existen en Square
        for mongo_product in mongo_products:
            if mongo_product.get("square_product_id") not in square_product_ids:
                print(f"Producto eliminado (no está en Square): {mongo_product['nombre']}")
                collection.delete_one({"_id": mongo_product["_id"]})

        # Comparar y actualizar o agregar productos
        for square_product_id, square_product in square_products.items():
            product_name = square_product["item_data"]["name"]
            price = None
            variations = square_product["item_data"].get("variations", [])
            if variations:
                # Obtenemos los datos de la variación
                variation_data = variations[0].get("item_variation_data", {})
                # Verificamos si existe "price_money" y que tenga la clave "amount"
                if "price_money" in variation_data and "amount" in variation_data["price_money"]:
                    price = variation_data["price_money"]["amount"] / 100

            category_ids = square_product["item_data"].get("category_ids", [])
            modifiers = square_product["item_data"].get("modifiers", [])

            # Datos del producto
            product_data = {
                "nombre": product_name,
                "categoria": category_ids,
                "precio": price,
                "modificadores": modifiers,
                "square_product_id": square_product_id  # Usamos el ID de Square como identificador único
            }

            # Buscar si el producto ya existe en MongoDB por el product_id de Square
            existing_product = collection.find_one({"square_product_id": square_product_id})

            if existing_product:
                # Si el producto existe, comparamos si hay cambios
                if (existing_product["precio"] != product_data["precio"] or
                    existing_product["categoria"] != product_data["categoria"] or
                    existing_product["modificadores"] != product_data["modificadores"]):
                    # Si hay cambios, lo actualizamos
                    collection.update_one(
                        {"_id": existing_product["_id"]},
                        {"$set": product_data}
                    )
                    print(f"Producto actualizado: {product_name}")
            else:
                # Si el producto no existe, lo insertamos
                collection.insert_one(product_data)
                print(f"Producto insertado: {product_name}")

        print("Datos sincronizados con éxito.")
    else:
        print(f"Error al sincronizar datos: {response.status_code} {response.text}")

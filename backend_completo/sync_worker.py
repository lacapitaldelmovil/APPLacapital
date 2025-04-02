
import time
from server import sync_all_data  # Asegúrate de tener esta función en server.py

while True:
    print("⏳ Sincronizando datos desde Square a MongoDB...")
    try:
        sync_all_data()
        print("✅ Sincronización completada. Esperando 1 hora...")
    except Exception as e:
        print(f"❌ Error durante la sincronización: {e}")
    time.sleep(3600)  # Espera una hora

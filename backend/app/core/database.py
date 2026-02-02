from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env (que crearemos ahora)
load_dotenv()

# Recuperamos la URI de las variables de entorno (¡Nunca hardcodeada en el código final!)
MONGO_URI = os.getenv("MONGO_URI")


class Database:
    client: MongoClient = None

    def connect(self):
        """Crea la conexión a la base de datos."""
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Ping para verificar conexión
            self.client.admin.command("ping")
            print("Conexión a MongoDB Atlas exitosa")
        except ConnectionFailure as e:
            print(f"Error de conexión a MongoDB: {e}")
            raise e

    def get_db(self):
        """Devuelve la instancia de la base de datos específica del proyecto."""
        if self.client is None:
            self.connect()
        # Aquí usamos el nombre de tu base de datos definido en tu script original
        return self.client["IA_2_2"]

    def close(self):
        """Cierra la conexión."""
        if self.client:
            self.client.close()
            print("Conexión a MongoDB cerrada")


# Instancia global para usar en el resto de la app
db = Database()

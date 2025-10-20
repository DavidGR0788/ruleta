import mysql.connector
import json
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, config_file=None):
        if config_file is None:
            # Buscar config file desde la raíz del proyecto
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_file = os.path.join(project_root, 'config', 'settings.json')
        self.config = self.load_config(config_file)
        self.connection = None
    
    def load_config(self, config_file):
        """Cargar configuración desde archivo JSON"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                print(f"✅ Configuración cargada desde: {config_file}")
                return config['database']
        except Exception as e:
            print(f"❌ Error cargando configuración desde {config_file}: {e}")
            # Configuración por defecto
            return {
                'host': 'localhost',
                'user': 'root',
                'password': '',
                'database': 'ruleta_db',
                'port': 3306
            }
    
    def connect(self):
        """Conectar a la base de datos MySQL"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            print("✅ Conectado a la base de datos MySQL")
            return True
        except mysql.connector.Error as e:
            print(f"❌ Error conectando a MySQL: {e}")
            return False
    
    def test_connection(self):
        """Probar la conexión y estructura de la base de datos"""
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Verificar tablas existentes
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("📊 Tablas en la base de datos:")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Verificar sesiones existentes
            cursor.execute("SELECT * FROM prediction_sessions")
            sessions = cursor.fetchall()
            print("🎯 Sesiones existentes:")
            for session in sessions:
                print(f"  - ID: {session[0]}, Nombre: {session[1]}, Activa: {session[5]}")
            
            # Verificar parámetros aprendidos
            cursor.execute("SELECT * FROM learned_parameters")
            parameters = cursor.fetchall()
            print("⚙️ Parámetros aprendidos:")
            for param in parameters:
                print(f"  - {param[1]}: {param[2]}")
            
            cursor.close()
            return True
            
        except mysql.connector.Error as e:
            print(f"❌ Error probando base de datos: {e}")
            return False

if __name__ == "__main__":
    # Probar la conexión
    print("🧪 Probando conexión a la base de datos...")
    db = DatabaseManager()
    if db.test_connection():
        print("🎉 ¡Conexión a base de datos exitosa!")
    else:
        print("❌ Falló la conexión a la base de datos")
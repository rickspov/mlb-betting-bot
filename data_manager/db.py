# db.py
# Módulo para gestionar la base de datos local SQLite para MLB Betting Bot.
# Permite crear y conectar a la base de datos, y define la tabla daily_roster para almacenar datos de rosters diarios.

import sqlite3
import os

# Nombre del archivo de la base de datos
DB_FILENAME = 'mlb_data.db'

# Ruta absoluta al archivo de la base de datos (en el mismo directorio que este script)
DB_PATH = os.path.join(os.path.dirname(__file__), DB_FILENAME)


def init_db():
    """
    Inicializa la base de datos y crea la tabla daily_roster si no existe.
    La tabla almacena información de los rosters diarios para apuestas MLB.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Crear la tabla daily_roster si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_roster (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            name TEXT,
            team TEXT,
            position TEXT,
            salary INTEGER,
            fppg REAL,
            games_played INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Base de datos inicializada y tabla 'daily_roster' lista en {DB_PATH}")

# Si se ejecuta este archivo directamente, inicializa la base de datos
def main():
    init_db()

if __name__ == "__main__":
    main() 
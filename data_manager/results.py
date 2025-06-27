# results.py
# Módulo para almacenar resultados diarios de jugadores en la base de datos mlb_data.db
# Permite insertar resultados individuales y en lote en la tabla daily_results

import sqlite3
import os
from data_manager.db import DB_PATH


def init_results_table():
    """
    Crea la tabla daily_results si no existe en la base de datos.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            player_name TEXT,
            actual_fppg REAL,
            is_mvp BOOLEAN,
            team TEXT
        )
    ''')
    conn.commit()
    conn.close()


def insert_result(date, player_name, actual_fppg, is_mvp, team):
    """
    Inserta el resultado de un jugador en la tabla daily_results usando una sentencia parametrizada.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO daily_results (date, player_name, actual_fppg, is_mvp, team)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, player_name, actual_fppg, int(is_mvp), team))
    conn.commit()
    conn.close()


def bulk_insert_results(results_list):
    """
    Inserta múltiples resultados en la tabla daily_results usando una sola conexión.
    results_list: lista de diccionarios con las claves: date, player_name, actual_fppg, is_mvp, team
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    data = [
        (
            r['date'], r['player_name'], r['actual_fppg'], int(r['is_mvp']), r['team']
        ) for r in results_list
    ]
    cursor.executemany('''
        INSERT INTO daily_results (date, player_name, actual_fppg, is_mvp, team)
        VALUES (?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()


def get_results_by_date(date):
    """
    Devuelve una lista de diccionarios con los resultados reales de la tabla daily_results para una fecha dada.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT player_name, actual_fppg, is_mvp, team
        FROM daily_results
        WHERE date = ?
    ''', (date,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Ejemplo de uso: insertar 3 resultados, uno como MVP
if __name__ == "__main__":
    from datetime import datetime
    # Inicializar la tabla si no existe
    init_results_table()

    today = datetime.today().strftime('%Y-%m-%d')
    resultados = [
        {
            'date': today,
            'player_name': 'Juan Soto',
            'actual_fppg': 15.2,
            'is_mvp': False,
            'team': 'SD'
        },
        {
            'date': today,
            'player_name': 'Aaron Judge',
            'actual_fppg': 18.7,
            'is_mvp': True,
            'team': 'NYY'
        },
        {
            'date': today,
            'player_name': 'Jose Altuve',
            'actual_fppg': 11.5,
            'is_mvp': False,
            'team': 'HOU'
        }
    ]

    # Inserción masiva de los resultados de ejemplo
    bulk_insert_results(resultados)
    print(f"Se insertaron {len(resultados)} resultados en la base de datos para la fecha {today}.") 
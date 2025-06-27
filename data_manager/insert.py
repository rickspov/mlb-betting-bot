# insert.py
# Módulo para insertar datos de jugadores en la base de datos daily_roster de MLB Betting Bot.
# Permite inserciones individuales y masivas (bulk) usando SQLite.

import sqlite3
from datetime import datetime
from data_manager.db import init_db, DB_PATH


def insert_player(date, name, team, position, salary, fppg, games_played):
    """
    Inserta un jugador en la tabla daily_roster usando una sentencia parametrizada.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO daily_roster (date, name, team, position, salary, fppg, games_played)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (date, name, team, position, salary, fppg, games_played))
    conn.commit()
    conn.close()


def bulk_insert_players(players_list):
    """
    Inserta múltiples jugadores en la tabla daily_roster usando una sola conexión.
    players_list: lista de diccionarios con las claves: date, name, team, position, salary, fppg, games_played
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    data = [
        (
            p['date'], p['name'], p['team'], p['position'],
            p['salary'], p['fppg'], p['games_played']
        ) for p in players_list
    ]
    cursor.executemany('''
        INSERT INTO daily_roster (date, name, team, position, salary, fppg, games_played)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()


# Ejemplo de uso: insertar 3 jugadores hardcodeados con la fecha de hoy
if __name__ == "__main__":
    # Inicializar la base de datos y la tabla si no existen
    init_db()

    today = datetime.today().strftime('%Y-%m-%d')
    jugadores = [
        {
            'date': today,
            'name': 'Juan Soto',
            'team': 'SD',
            'position': 'OF',
            'salary': 9500,
            'fppg': 12.1,
            'games_played': 120
        },
        {
            'date': today,
            'name': 'Aaron Judge',
            'team': 'NYY',
            'position': 'OF',
            'salary': 10500,
            'fppg': 14.3,
            'games_played': 110
        },
        {
            'date': today,
            'name': 'Jose Altuve',
            'team': 'HOU',
            'position': '2B',
            'salary': 8700,
            'fppg': 11.0,
            'games_played': 115
        }
    ]

    # Inserción masiva de los jugadores de ejemplo
    bulk_insert_players(jugadores)
    print(f"Se insertaron {len(jugadores)} jugadores en la base de datos para la fecha {today}.") 
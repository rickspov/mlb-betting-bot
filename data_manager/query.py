# query.py
# Módulo para consultar jugadores de la base de datos daily_roster de MLB Betting Bot.
# Permite obtener los jugadores activos para una fecha específica como lista de diccionarios.

import sqlite3
from typing import List, Dict
from data_manager.db import DB_PATH


def get_players_by_date(date: str) -> List[Dict]:
    """
    Consulta todos los jugadores activos para una fecha dada en la tabla daily_roster.
    Devuelve una lista de diccionarios con los campos: name, salary, fppg, position, team, games_played.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder a los resultados como diccionarios
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name, salary, fppg, position, team, games_played
        FROM daily_roster
        WHERE date = ?
    ''', (date,))
    rows = cursor.fetchall()
    players = [dict(row) for row in rows]
    conn.close()
    return players


# Ejemplo de uso: consultar jugadores para la fecha de hoy
if __name__ == "__main__":
    from datetime import datetime
    today = datetime.today().strftime('%Y-%m-%d')
    print(f"Jugadores activos para la fecha {today}:")
    jugadores = get_players_by_date(today)
    for i, jugador in enumerate(jugadores, 1):
        print(f"{i}. {jugador['name']} | {jugador['position']} | {jugador['team']} | Salario: ${jugador['salary']} | FPPG: {jugador['fppg']} | Juegos: {jugador['games_played']}") 
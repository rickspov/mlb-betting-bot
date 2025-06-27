# player_stats_fetcher.py
# Este módulo se encarga de obtener y procesar estadísticas de jugadores para su uso en la optimización de alineaciones DFS. 

from typing import List, Dict


def get_mock_player_stats() -> List[Dict]:
    """
    Devuelve una lista de diccionarios con estadísticas ficticias de jugadores para pruebas.
    Cada diccionario representa un jugador con los campos:
        - name: Nombre del jugador (str)
        - salary: Salario en FanDuel (int, en miles)
        - fppg: Fantasy Points Per Game promedio (float)
        - position: Posición del jugador (str)
        - team: Equipo del jugador (str)
    """
    players = [
        {"name": "Mike Trout", "salary": 9500, "fppg": 12.3, "position": "OF", "team": "LAA"},
        {"name": "Mookie Betts", "salary": 10200, "fppg": 13.1, "position": "OF", "team": "LAD"},
        {"name": "Shohei Ohtani", "salary": 11000, "fppg": 15.2, "position": "P", "team": "LAA"},
        {"name": "Freddie Freeman", "salary": 9200, "fppg": 11.8, "position": "1B", "team": "LAD"},
        {"name": "Jose Ramirez", "salary": 8700, "fppg": 10.9, "position": "3B", "team": "CLE"},
        {"name": "Vladimir Guerrero Jr.", "salary": 9000, "fppg": 11.2, "position": "1B", "team": "TOR"},
        {"name": "Trea Turner", "salary": 8800, "fppg": 10.7, "position": "SS", "team": "PHI"},
        {"name": "Ronald Acuña Jr.", "salary": 10500, "fppg": 14.0, "position": "OF", "team": "ATL"},
        {"name": "Pete Alonso", "salary": 8600, "fppg": 10.5, "position": "1B", "team": "NYM"},
        {"name": "Julio Rodriguez", "salary": 9300, "fppg": 12.0, "position": "OF", "team": "SEA"},
    ]
    return players

# La función get_mock_player_stats puede ser importada y utilizada en otros módulos para pruebas y desarrollo. 
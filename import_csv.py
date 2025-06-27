import csv
from data_manager.insert import bulk_insert_players

# Ruta al archivo CSV (ajusta si lo mueves)
CSV_PATH = "roster_2024_06_20.csv"


def read_csv_to_dicts(file_path):
    """
    Lee un archivo CSV y convierte cada fila en un diccionario con los tipos de datos correctos.
    Retorna una lista de diccionarios.
    """
    players = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Convertir los campos numéricos a los tipos adecuados
            player = {
                'date': row['date'],
                'name': row['name'],
                'team': row['team'],
                'position': row['position'],
                'salary': int(row['salary']),
                'fppg': float(row['fppg']),
                'games_played': int(row['games_played'])
            }
            players.append(player)
    return players


if __name__ == "__main__":
    # Leer los datos del CSV y convertirlos a una lista de diccionarios
    players_data = read_csv_to_dicts(CSV_PATH)
    # Insertar todos los jugadores en la base de datos usando bulk_insert_players
    bulk_insert_players(players_data)
    # Imprimir mensaje de éxito con la cantidad de jugadores importados
    print(f"{len(players_data)} jugadores importados correctamente desde {CSV_PATH}") 
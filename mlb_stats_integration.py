import statsapi
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import numpy as np
from typing import List, Dict
import os
from datetime import datetime, timedelta
import random

# =====================
# Extracción de datos MLB
# =====================

def get_todays_games():
    """
    Extrae los partidos del día usando MLB-StatsAPI.
    Retorna una lista de diccionarios con info básica de cada partido.
    """
    schedule = statsapi.schedule(date=None, sportId=1)  # MLB sportId=1
    games = []
    for game in schedule:
        games.append({
            'game_id': game['game_id'],
            'home_name': game['home_name'],
            'away_name': game['away_name'],
            'game_date': game['game_date'],
            'venue_name': game['venue_name']
        })
    return games

def get_team_stats(team_name):
    """
    Extrae estadísticas ofensivas y de lanzadores para un equipo dado.
    Retorna un diccionario con stats relevantes.
    """
    # Ejemplo: statsapi.team_stats(teamId, type='season', season=2024)
    # Aquí simulamos stats relevantes para el ejemplo
    # En producción, usar statsapi y mapear los campos necesarios
    return {
        'avg_runs': np.random.uniform(3, 6),
        'avg_hits': np.random.uniform(7, 10),
        'avg_hr': np.random.uniform(0.8, 1.5),
        'era': np.random.uniform(3, 5),
        'whip': np.random.uniform(1.1, 1.4)
    }

# Diccionario de mapeo de nombres de equipos de statsapi a Baseball Reference
TEAM_NAME_MAP = {
    'Arizona Diamondbacks': 'Diamondbacks',
    'Atlanta Braves': 'Braves',
    'Baltimore Orioles': 'Orioles',
    'Boston Red Sox': 'Red Sox',
    'Chicago White Sox': 'White Sox',
    'Chicago Cubs': 'Cubs',
    'Cincinnati Reds': 'Reds',
    'Cleveland Guardians': 'Guardians',
    'Colorado Rockies': 'Rockies',
    'Detroit Tigers': 'Tigers',
    'Houston Astros': 'Astros',
    'Kansas City Royals': 'Royals',
    'Los Angeles Angels': 'Angels',
    'Los Angeles Dodgers': 'Dodgers',
    'Miami Marlins': 'Marlins',
    'Milwaukee Brewers': 'Brewers',
    'Minnesota Twins': 'Twins',
    'New York Yankees': 'Yankees',
    'New York Mets': 'Mets',
    'Oakland Athletics': 'Athletics',
    'Philadelphia Phillies': 'Phillies',
    'Pittsburgh Pirates': 'Pirates',
    'San Diego Padres': 'Padres',
    'San Francisco Giants': 'Giants',
    'Seattle Mariners': 'Mariners',
    'St. Louis Cardinals': 'Cardinals',
    'Tampa Bay Rays': 'Rays',
    'Texas Rangers': 'Rangers',
    'Toronto Blue Jays': 'Blue Jays',
    'Washington Nationals': 'Nationals',
}

def get_team_stats_bref(team_name: str) -> dict:
    """
    Obtiene estadísticas reales de un equipo desde el CSV de Baseball Reference 2025.
    Retorna un diccionario con stats relevantes para Over/Under.
    """
    try:
        df = pd.read_csv(BREF_CSV)
        # Usar el nombre mapeado si existe
        bref_name = TEAM_NAME_MAP.get(team_name, team_name)
        # Normalizar nombre de equipo para buscar
        team_row = df[df['Tm'].str.lower() == bref_name.lower()]
        if team_row.empty:
            # Intentar búsqueda parcial (por si hay diferencias menores)
            team_row = df[df['Tm'].str.contains(bref_name, case=False, na=False)]
        if team_row.empty:
            raise ValueError(f"No se encontró el equipo {team_name} (mapeado: {bref_name}) en el CSV de Baseball Reference.")
        row = team_row.iloc[0]
        # Calcular stats clave
        avg_runs = float(row['R']) / float(row['G']) if float(row['G']) > 0 else 4.0
        era = float(row['ERA'])
        whip = float(row['WHIP'])
        return {
            'avg_runs': round(avg_runs, 2),
            'era': round(era, 2),
            'whip': round(whip, 2),
            'total_runs': int(row['R']),
            'games_played': int(row['G'])
        }
    except Exception as e:
        print(f"Error obteniendo stats de Baseball Reference para {team_name}: {e}")
        # Fallback a stats simuladas
        return get_team_stats(team_name)

def get_match_real_stats(game: dict) -> dict:
    """
    Dado un diccionario de partido, extrae y combina stats reales de ambos equipos usando Baseball Reference.
    Retorna un diccionario listo para predicción Over/Under.
    """
    home_stats = get_team_stats_bref(game['home_name'])
    away_stats = get_team_stats_bref(game['away_name'])
    match_data = {
        'home_team': game['home_name'],
        'away_team': game['away_name'],
        'game_date': game.get('game_date', ''),
        'venue': game.get('venue_name', ''),
        # Stats reales de ambos equipos
        'home_avg_runs': home_stats['avg_runs'],
        'away_avg_runs': away_stats['avg_runs'],
        'home_era': home_stats['era'],
        'away_era': away_stats['era'],
        'home_whip': home_stats['whip'],
        'away_whip': away_stats['whip'],
        # Información adicional
        'home_total_runs': home_stats['total_runs'],
        'away_total_runs': away_stats['total_runs'],
        'home_games_played': home_stats['games_played'],
        'away_games_played': away_stats['games_played']
    }
    return match_data

# =====================
# NUEVAS FUNCIONES PARA EL SPRINT
# =====================

def get_player_game_stats(game_id: str) -> Dict:
    """
    Extrae estadísticas por jugador de un juego específico.
    Retorna diccionario con stats por player_id.
    """
    try:
        boxscore = statsapi.boxscore_data(game_id)
        player_stats = {}
        
        # Procesar jugadores home
        if 'home' in boxscore and 'players' in boxscore['home']:
            for player_id, player_data in boxscore['home']['players'].items():
                if 'stats' in player_data and 'batting' in player_data['stats']:
                    batting_stats = player_data['stats']['batting']
                    player_stats[player_id] = {
                        'name': player_data.get('person', {}).get('fullName', ''),
                        'team': boxscore['home'].get('teamName', ''),
                        'ab': batting_stats.get('atBats', 0),
                        'h': batting_stats.get('hits', 0),
                        'hr': batting_stats.get('homeRuns', 0),
                        'r': batting_stats.get('runs', 0),
                        'rbi': batting_stats.get('rbi', 0),
                        'bb': batting_stats.get('baseOnBalls', 0),
                        'so': batting_stats.get('strikeOuts', 0),
                        'sb': batting_stats.get('stolenBases', 0),
                        'obp': batting_stats.get('obp', 0.0),
                        'slg': batting_stats.get('slg', 0.0)
                    }
        
        # Procesar jugadores away
        if 'away' in boxscore and 'players' in boxscore['away']:
            for player_id, player_data in boxscore['away']['players'].items():
                if 'stats' in player_data and 'batting' in player_data['stats']:
                    batting_stats = player_data['stats']['batting']
                    player_stats[player_id] = {
                        'name': player_data.get('person', {}).get('fullName', ''),
                        'team': boxscore['away'].get('teamName', ''),
                        'ab': batting_stats.get('atBats', 0),
                        'h': batting_stats.get('hits', 0),
                        'hr': batting_stats.get('homeRuns', 0),
                        'r': batting_stats.get('runs', 0),
                        'rbi': batting_stats.get('rbi', 0),
                        'bb': batting_stats.get('baseOnBalls', 0),
                        'so': batting_stats.get('strikeOuts', 0),
                        'sb': batting_stats.get('stolenBases', 0),
                        'obp': batting_stats.get('obp', 0.0),
                        'slg': batting_stats.get('slg', 0.0)
                    }
        
        return player_stats
    except Exception as e:
        print(f"Error obteniendo stats del juego {game_id}: {e}")
        return {}

def get_weather_and_stadium(game_id: str) -> Dict:
    """
    Obtiene información del clima y estadio para un juego específico.
    Retorna diccionario con temp, wind, conditions, stadium_name, is_dome.
    """
    try:
        # Obtener información del juego
        game_data = statsapi.get('game', {'gamePk': game_id})
        venue_info = game_data.get('gameData', {}).get('venue', {})
        
        # Información del estadio
        stadium_name = venue_info.get('name', 'Unknown')
        is_dome = venue_info.get('indoor', False)
        
        # Información del clima (si está disponible)
        weather_info = game_data.get('gameData', {}).get('weather', {})
        temp_celsius = weather_info.get('temp', 20)  # Default 20°C
        wind_kph = weather_info.get('wind', {}).get('speed', {}).get('value', 0)
        conditions = weather_info.get('condition', 'Unknown')
        
        return {
            'stadium_name': stadium_name,
            'is_dome': is_dome,
            'temp_celsius': temp_celsius,
            'wind_kph': wind_kph,
            'conditions': conditions
        }
    except Exception as e:
        print(f"Error obteniendo clima/estadio para juego {game_id}: {e}")
        return {
            'stadium_name': 'Unknown',
            'is_dome': False,
            'temp_celsius': 20,
            'wind_kph': 0,
            'conditions': 'Unknown'
        }

def update_daily_player_stats(fecha: str) -> str:
    """
    Genera/actualiza archivo CSV con stats diarios de jugadores.
    Retorna ruta del archivo generado.
    """
    try:
        # Obtener juegos del día
        juegos = statsapi.schedule(date=fecha)
        all_player_stats = []
        
        for juego in juegos:
            game_id = juego['game_id']
            player_stats = get_player_game_stats(game_id)
            
            for player_id, stats in player_stats.items():
                stats['date'] = fecha
                stats['game_id'] = game_id
                all_player_stats.append(stats)
        
        # Crear DataFrame y guardar
        if all_player_stats:
            df = pd.DataFrame(all_player_stats)
            os.makedirs('data', exist_ok=True)
            filename = f"data/player_stats_daily_{fecha.replace('-', '')}.csv"
            df.to_csv(filename, index=False)
            return filename
        else:
            return ""
            
    except Exception as e:
        print(f"Error actualizando stats diarios para {fecha}: {e}")
        return ""

# =====================
# Modelo de predicción Over/Under
# =====================

class OverUnderPredictor:
    """
    Modelo simple para predecir el total de carreras en un partido MLB.
    Usa RandomForestRegressor como ejemplo.
    """
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.is_trained = False

    def fit(self, X, y):
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, match_data):
        """
        match_data: dict con features del partido
        """
        X = pd.DataFrame([match_data])
        # Selecciona solo las columnas numéricas relevantes
        features = ['home_avg_runs', 'away_avg_runs', 'home_era', 'away_era', 'home_whip', 'away_whip']
        return float(self.model.predict(X[features])[0])

# Instancia global para demo
predictor = OverUnderPredictor()

def train_over_under_model():
    """
    Entrena el modelo con datos simulados (en producción usar históricos reales).
    """
    np.random.seed(42)
    n = 200
    X = pd.DataFrame({
        'home_avg_runs': np.random.uniform(3, 6, n),
        'away_avg_runs': np.random.uniform(3, 6, n),
        'home_era': np.random.uniform(3, 5, n),
        'away_era': np.random.uniform(3, 5, n),
        'home_whip': np.random.uniform(1.1, 1.4, n),
        'away_whip': np.random.uniform(1.1, 1.4, n),
    })
    y = (
        X['home_avg_runs'] + X['away_avg_runs']
        + np.random.normal(0, 1, n)
    )
    predictor.fit(X, y)

# Entrena el modelo al importar el módulo
train_over_under_model()

def predict_over_under(match_data):
    """
    Recibe un dict con datos de partido y retorna la predicción de carreras totales.
    """
    return predictor.predict(match_data)

# =====================
# Ejemplo de flujo principal
# =====================

if __name__ == "__main__":
    print("Extrayendo partidos del día...")
    games = get_todays_games()
    for game in games:
        match_data = get_match_real_stats(game)
        pred = predict_over_under(match_data)
        print(f"{match_data['away_team']} @ {match_data['home_team']} ({match_data['game_date']}): Predicción Over/Under = {pred:.2f}")

# =============================
# Integración MLB-StatsAPI
# =============================

def obtener_partidos_con_probabilidades(fecha: str) -> List[Dict]:
    """
    Retorna lista de partidos del día con equipos y probabilidad Over/Under si está disponible.
    """
    juegos = statsapi.schedule(date=fecha)
    partidos = []
    for juego in juegos:
        partidos.append({
            'home_team': juego['home_name'],
            'away_team': juego['away_name'],
            'over_under': juego.get('overUnder', None),  # puede ser None si no está
            'start_time': juego['game_datetime']
        })
    return partidos

def obtener_alineaciones_confirmadas(fecha: str) -> Dict[str, List[Dict]]:
    """
    Retorna diccionario de alineaciones confirmadas por equipo para la fecha dada.
    """
    juegos = statsapi.schedule(date=fecha)
    alineaciones = {}
    for juego in juegos:
        # Obtener IDs de equipos
        home_id = juego['home_id']
        away_id = juego['away_id']
        # Obtener roster (alineación confirmada) para cada equipo
        home_roster = statsapi.roster(home_id, rosterType='active')
        away_roster = statsapi.roster(away_id, rosterType='active')
        alineaciones[juego['home_name']] = home_roster
        alineaciones[juego['away_name']] = away_roster
    return alineaciones

def obtener_datos_para_optimizacion(fecha: str) -> List[Dict]:
    """
    Prepara datos de jugadores con stats y atributos para alimentar optimize_lineup.
    Retorna lista de dicts compatibles con el optimizador.
    """
    alineaciones = obtener_alineaciones_confirmadas(fecha)
    jugadores_opt = []
    for equipo, roster in alineaciones.items():
        for jugador in roster:
            # Simulación: en producción, extraer stats reales y salario
            jugadores_opt.append({
                'date': fecha,
                'name': jugador['person']['fullName'],
                'team': equipo,
                'position': jugador['position']['abbreviation'],
                'salary': int(8000 + 4000 * np.random.rand()),  # Simula salario
                'fppg': round(5 + 10 * np.random.rand(), 2),    # Simula FPPG
                'games_played': int(10 + 30 * np.random.rand()) # Simula juegos jugados
            })
    return jugadores_opt

# =============================
# Ejemplo de uso en flujo principal
# =============================
if __name__ == "__main__":
    fecha = pd.Timestamp.today().strftime('%Y-%m-%d')
    print("Partidos con Over/Under:")
    for p in obtener_partidos_con_probabilidades(fecha):
        print(f"{p['away_team']} @ {p['home_team']} - Over/Under: {p['over_under']}")
    print("\nAlineaciones confirmadas:")
    alineaciones = obtener_alineaciones_confirmadas(fecha)
    for equipo, roster in alineaciones.items():
        print(equipo, [j['person']['fullName'] for j in roster])
    print("\nDatos para optimización:")
    jugadores = obtener_datos_para_optimizacion(fecha)
    print(jugadores[:3], "...")

BREF_CSV = "data/bref_team_stats_2025.csv" 
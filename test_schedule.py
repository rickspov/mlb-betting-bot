import statsapi
from datetime import datetime, timedelta

# Probar con la fecha de ayer para ver partidos finalizados
fecha_ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
print(f"Probando con fecha: {fecha_ayer}")

try:
    juegos = statsapi.schedule(date=fecha_ayer)
    print(f"Encontrados {len(juegos)} juegos")
    
    for i, juego in enumerate(juegos[:3]):  # Solo los primeros 3
        print(f"\nJuego {i+1}:")
        print(f"  ID: {juego.get('game_id')}")
        print(f"  Equipos: {juego.get('away_name')} @ {juego.get('home_name')}")
        print(f"  Estado: {juego.get('status')}")
        print(f"  Fecha: {juego.get('game_date')}")
        print(f"  Hora: {juego.get('game_datetime')}")
        
        # Verificar si hay información del score en el schedule
        if 'away_score' in juego:
            print(f"  Score Away: {juego.get('away_score')}")
        if 'home_score' in juego:
            print(f"  Score Home: {juego.get('home_score')}")
        
        # Si el juego está finalizado, probar boxscore
        if juego.get('status') == 'Final':
            try:
                boxscore = statsapi.boxscore_data(juego['game_id'])
                home_runs = boxscore['home']['runs']
                away_runs = boxscore['away']['runs']
                print(f"  Boxscore - Away: {away_runs}, Home: {home_runs}")
            except Exception as e:
                print(f"  Error obteniendo boxscore: {e}")
        
        # Mostrar todas las claves disponibles
        print(f"  Claves disponibles: {list(juego.keys())}")
        
except Exception as e:
    print(f"Error: {e}") 
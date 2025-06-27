# compare_results.py
# Módulo para comparar la alineación optimizada con los resultados reales de la base de datos.
# Permite evaluar el rendimiento diario del bot de apuestas MLB.

import sqlite3
from typing import Dict, List
from data_manager.db import DB_PATH


def compare_lineup_vs_actual(date: str, predicted_lineup: Dict):
    """
    Compara la alineación optimizada con los resultados reales de la fecha indicada.
    Args:
        date (str): Fecha en formato 'YYYY-MM-DD'.
        predicted_lineup (dict): Resultado de optimize_lineup().
    Returns:
        dict: Métricas de comparación y evaluación.
    """
    # Conectar a la base de datos y obtener resultados reales de la fecha
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT player_name, actual_fppg, is_mvp
        FROM daily_results
        WHERE date = ?
    ''', (date,))
    rows = cursor.fetchall()
    conn.close()

    if not rows or len(rows) < 7:
        print(f"❌ No hay suficientes resultados reales para la fecha {date}.")
        return None

    # Ordenar por actual_fppg descendente para encontrar el equipo ganador real
    sorted_rows = sorted(rows, key=lambda r: r['actual_fppg'], reverse=True)
    real_mvp = sorted_rows[0]['player_name']
    real_team = [r['player_name'] for r in sorted_rows[:7]]
    real_team_fppg = sum(r['actual_fppg'] for r in sorted_rows[:7])

    # Extraer alineación predicha
    pred_mvp = predicted_lineup.get('mvp')
    pred_utilities = predicted_lineup.get('utility', [])
    pred_team = [pred_mvp] + pred_utilities if pred_mvp else pred_utilities

    # Calcular métricas
    acertado_mvp = pred_mvp == real_mvp
    jugadores_coincidentes = len(set(pred_team) & set(real_team))

    # FPPG real de la alineación predicha
    fppg_dict = {r['player_name']: r['actual_fppg'] for r in rows}
    pred_team_fppg = sum(fppg_dict.get(j, 0) for j in pred_team)
    diferencia = pred_team_fppg - real_team_fppg

    # Resultados
    result = {
        'acertado_mvp': acertado_mvp,
        'jugadores_coincidentes': jugadores_coincidentes,
        'fppg_total_predicho': round(pred_team_fppg, 2),
        'fppg_total_real': round(real_team_fppg, 2),
        'diferencia_puntos': round(diferencia, 2),
        'real_mvp': real_mvp,
        'real_team': real_team
    }

    # Impresión formateada
    print("\n===== COMPARACIÓN DE RESULTADOS =====")
    print(f"🗓️ Fecha: {date}")
    print(f"🏆 MVP predicho: {pred_mvp}")
    print(f"🏆 MVP real: {real_mvp}")
    print(f"{'✅' if acertado_mvp else '❌'} ¿Acierto MVP?: {acertado_mvp}")
    print(f"👥 Jugadores coincidentes: {jugadores_coincidentes} de 7")
    print(f"📊 FPPG total alineación predicha: {result['fppg_total_predicho']}")
    print(f"📊 FPPG total equipo real: {result['fppg_total_real']}")
    print(f"📊 Diferencia de puntos: {result['diferencia_puntos']}")
    print("====================================\n")

    return result


# Ejemplo de uso (requiere datos en daily_results y una alineación predicha)
if __name__ == "__main__":
    # Ejemplo de alineación predicha (ajustar según tus datos)
    ejemplo_prediccion = {
        'mvp': 'Aaron Judge',
        'utility': ['Juan Soto', 'Jose Altuve', 'Mike Trout', 'Mookie Betts', 'Freddie Freeman', 'Trea Turner']
    }
    from datetime import datetime
    today = datetime.today().strftime('%Y-%m-%d')
    compare_lineup_vs_actual(today, ejemplo_prediccion) 
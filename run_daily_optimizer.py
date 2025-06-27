# run_daily_optimizer.py
# Script para ejecutar el optimizador diario usando datos reales de la base de datos.
# Usa una fecha hardcodeada para todas las consultas y mensajes.

from dfs_optimizer.optimize_lineup import optimize_lineup
from data_manager.query import get_players_by_date

# Cantidad mínima de jugadores requeridos para la optimización
MIN_PLAYERS_REQUIRED = 7

# 1. Fecha del juego a optimizar (hardcodeada)
target_date = "2024-06-20"  # Cambia esta fecha según sea necesario

def run_optimizer(players_data=None):
    """
    Ejecuta la optimización diaria para la fecha hardcodeada o con datos externos.
    Si players_data es None, usa la base local; si se pasa una lista, la usa directamente.
    Retorna un diccionario con claves 'status', 'mvp', 'lineup', etc.
    """
    if players_data is not None:
        jugadores = players_data
    else:
        jugadores = get_players_by_date(target_date)
    if len(jugadores) < MIN_PLAYERS_REQUIRED:
        return {
            "status": "error",
            "message": f"No hay suficientes jugadores para la optimización. Se requieren al menos {MIN_PLAYERS_REQUIRED}."
        }
    result = optimize_lineup(players_data=jugadores)
    return result

if __name__ == "__main__":
    result = run_optimizer()
    if result.get("status") == "success":
        mvp = result.get('mvp', {})
        utility = result.get('utility', [])
        salary = result.get('salary_used', 0)
        projected = result.get('projected_points', 0)
        print(f"\n✅ Alineación óptima para {target_date}")
        print(f"🏆 MVP: {mvp.get('name', '')} (${mvp.get('salary', 0)}) | FPPG: {mvp.get('fppg', 0)}")
        print("👥 Jugadores utility:")
        for i, p in enumerate(utility, start=1):
            nombre = p.get('name', '') if isinstance(p, dict) else ''
            salario = p.get('salary', 0) if isinstance(p, dict) else 0
            fppg = p.get('fppg', 0) if isinstance(p, dict) else 0
            print(f"  {i}. {nombre} (${salario}) | FPPG: {fppg}")
        print(f"\n💰 Salario total: ${salary}")
        print(f"📊 Puntos proyectados totales: {projected:.2f}")
    else:
        print(f"❌ Error en la optimización: {result.get('message', 'Error desconocido.')}")

# Nota: No se usa datetime.now() para evitar confusión con la fecha optimizada 
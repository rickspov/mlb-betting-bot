# optimize_lineup.py
# Este módulo contiene funciones para optimizar alineaciones de Daily Fantasy Sports (DFS) usando algoritmos de optimización.

from pulp import LpProblem, LpVariable, LpMaximize, lpSum, LpBinary, LpStatus
from dfs_optimizer.player_stats_fetcher import get_mock_player_stats
from typing import List, Dict, Optional


def optimize_lineup(players_data: Optional[List[Dict]] = None):
    """
    Optimiza una alineación DFS seleccionando 1 MVP (FPPG x1.5) y 5 utilities,
    maximizando la suma de FPPG ajustada bajo un presupuesto de 60,000.

    Args:
        players_data (opcional): Lista de diccionarios con datos de jugadores. Si es None, usa datos mock.

    Returns:
        dict: Diccionario con mvp, utility, salary_used, projected_points y status.
    """
    # Si no se pasa una lista de jugadores, usar los datos mock por defecto
    if players_data is None:
        players = get_mock_player_stats()
    else:
        players = players_data
    n = len(players)
    budget = 60000
    mvp_count = 1
    utility_count = 5

    # Crear el problema de optimización lineal
    prob = LpProblem("DFS_Lineup_Optimization", LpMaximize)

    # Variables binarias para cada jugador
    # mvp_vars[i] = 1 si el jugador i es seleccionado como MVP, 0 en caso contrario
    # utility_vars[i] = 1 si el jugador i es seleccionado como utility, 0 en caso contrario
    mvp_vars = [LpVariable(f"mvp_{i}", cat=LpBinary) for i in range(n)]
    utility_vars = [LpVariable(f"utility_{i}", cat=LpBinary) for i in range(n)]

    # Restricción 1: Seleccionar exactamente un MVP
    prob += lpSum(mvp_vars) == mvp_count, "Exactamente_un_MVP"
    
    # Restricción 2: Seleccionar exactamente 5 utilities
    prob += lpSum(utility_vars) == utility_count, "Exactamente_cinco_utilities"
    
    # Restricción 3: Un jugador no puede ser MVP y utility a la vez (no repeticiones)
    for i in range(n):
        prob += mvp_vars[i] + utility_vars[i] <= 1, f"No_repetir_jugador_{i}"
    
    # Restricción 4: Presupuesto total no debe superar 60,000 (MVP cuesta 1.5x)
    total_salary = lpSum([
        mvp_vars[i] * players[i]['salary'] * 1.5 + utility_vars[i] * players[i]['salary']
        for i in range(n)
    ])
    prob += total_salary <= budget, "Presupuesto_maximo"

    # Función objetivo: maximizar FPPG total ajustado
    # MVP: FPPG * 1.5, Utilities: FPPG * 1.0
    objective = lpSum([
        mvp_vars[i] * players[i]['fppg'] * 1.5 + utility_vars[i] * players[i]['fppg']
        for i in range(n)
    ])
    prob += objective, "Maximizar_FPPG_total"

    # Resolver el problema de optimización
    prob.solve()

    # Verificar si se encontró una solución factible
    if prob.status != 1:  # 1 = Optimal
        return {
            "mvp": None,
            "utility": [],
            "salary_used": 0,
            "projected_points": 0,
            "status": "error",
            "message": f"No se encontró una solución factible. Status: {LpStatus[prob.status]}"
        }

    # Procesar resultados de la solución óptima
    mvp = None
    utility = []
    salary_used = 0
    projected_points = 0
    
    # Extraer los jugadores seleccionados de la solución
    for i in range(n):
        if mvp_vars[i].varValue == 1:
            mvp = players[i]  # Guardar el dict completo del jugador MVP
            salary_used += players[i]['salary'] * 1.5
            projected_points += players[i]['fppg'] * 1.5
        elif utility_vars[i].varValue == 1:
            utility.append(players[i])  # Guardar el dict completo del jugador utility
            salary_used += players[i]['salary']
            projected_points += players[i]['fppg']

    # Crear resultado final con las claves exactas solicitadas
    result = {
        "mvp": mvp,
        "utility": utility,
        "salary_used": int(salary_used),
        "projected_points": round(projected_points, 2),
        "status": "success"
    }

    # Imprimir resultados de forma clara y organizada
    print("\n" + "="*50)
    print("RESULTADO DE LA OPTIMIZACIÓN DFS")
    print("="*50)
    print(f"Status: {result['status']}")
    print(f"\nMVP seleccionado: {result['mvp']['name']}")
    print(f"Jugadores utility ({len(result['utility'])}):")
    for i, jugador in enumerate(result['utility'], 1):
        print(f"  {i}. {jugador['name']}")
    print(f"\nSalario total usado: ${result['salary_used']:,}")
    print(f"Puntos proyectados totales: {result['projected_points']}")
    print("="*50)

    return result


def main():
    """
    Función principal para ejecutar la optimización cuando se corre el script directamente.
    """
    optimize_lineup()


if __name__ == "__main__":
    main() 
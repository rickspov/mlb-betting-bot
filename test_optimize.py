# test_optimize.py
# Script de prueba para la función de optimización de alineaciones DFS.
# Ejecuta la optimización y muestra un resumen limpio de los resultados.

from dfs_optimizer.optimize_lineup import optimize_lineup


def main():
    """
    Ejecuta la optimización de alineación y muestra un resumen limpio de los resultados.
    Maneja casos de éxito y fallo de forma clara.
    """
    # Ejecutar la optimización
    result = optimize_lineup()
    
    # Imprimir resumen limpio y bien formateado
    print("\n" + "="*60)
    print("RESUMEN DE OPTIMIZACIÓN DFS")
    print("="*60)
    
    # Estado de la optimización
    print(f"Estado: {result['status']}")
    
    # Verificar si se encontró una solución
    if result['mvp'] is None:
        print("\n❌ No se encontró una solución factible.")
        print("   Verifica las restricciones y datos de entrada.")
    else:
        print("\n✅ Optimización completada exitosamente")
        
        # MVP seleccionado
        print(f"\n🏆 MVP: {result['mvp']}")
        
        # Jugadores utility numerados
        print(f"\n👥 Jugadores utility ({len(result['utility'])}):")
        for i, player in enumerate(result['utility'], 1):
            print(f"   {i}. {player}")
        
        # Salario total con formato en dólares
        print(f"\n💰 Salario total: ${result['salary_used']:,}")
        
        # Puntos proyectados totales
        print(f"📊 Puntos proyectados: {result['projected_points']}")
    
    print("="*60)


if __name__ == "__main__":
    main() 
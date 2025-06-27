#!/usr/bin/env python3
"""
Automation Script: Daily Over/Under Model Retraining
===================================================
Script para re-entrenar automáticamente el modelo Over/Under cada noche.
Puede ser ejecutado manualmente o configurado con crontab.
"""

import sys
import os
import logging
from datetime import datetime, timedelta
import pandas as pd

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mlb_stats_integration import update_daily_player_stats
from over_under_model import retrain_daily, create_over_under_dataset

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automations/retrain_log.txt'),
        logging.StreamHandler()
    ]
)

def main():
    """
    Función principal que ejecuta el re-entrenamiento diario.
    """
    try:
        logging.info("Iniciando re-entrenamiento diario del modelo Over/Under")
        
        # 1. Actualizar stats de jugadores del día anterior
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        logging.info(f"Actualizando stats de jugadores para {yesterday}")
        
        stats_file = update_daily_player_stats(yesterday)
        if stats_file:
            logging.info(f"Stats actualizados guardados en: {stats_file}")
        else:
            logging.warning("No se pudieron actualizar stats de jugadores")
        
        # 2. Crear dataset Over/Under para el día anterior
        logging.info(f"Creando dataset Over/Under para {yesterday}")
        dataset = create_over_under_dataset(yesterday)
        
        if not dataset.empty:
            # Guardar dataset
            os.makedirs('data', exist_ok=True)
            dataset_file = f"data/over_under_daily_{yesterday.replace('-', '')}.csv"
            dataset.to_csv(dataset_file, index=False)
            logging.info(f"Dataset guardado en: {dataset_file}")
        else:
            logging.warning("No se pudo crear dataset Over/Under")
        
        # 3. Re-entrenar modelo
        logging.info("Iniciando re-entrenamiento del modelo")
        result = retrain_daily()
        
        if result['success']:
            logging.info(f"Modelo re-entrenado exitosamente")
            logging.info(f"MAE: {result['mae']:.2f}")
            logging.info(f"RMSE: {result['rmse']:.2f}")
            
            # Guardar métricas de rendimiento
            metrics_file = f"data/model_metrics_{datetime.now().strftime('%Y%m%d')}.json"
            import json
            with open(metrics_file, 'w') as f:
                json.dump(result, f, indent=2)
            logging.info(f"Métricas guardadas en: {metrics_file}")
            
        else:
            logging.error(f"Error en re-entrenamiento: {result.get('error', 'Unknown error')}")
            return 1
        
        logging.info("Re-entrenamiento diario completado exitosamente")
        return 0
        
    except Exception as e:
        logging.error(f"Error crítico en re-entrenamiento diario: {e}")
        return 1

def cleanup_old_files():
    """
    Limpia archivos antiguos para mantener el espacio de disco.
    """
    try:
        import glob
        from datetime import datetime, timedelta
        
        # Limpiar logs antiguos (más de 30 días)
        log_files = glob.glob('automations/retrain_log_*.txt')
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for log_file in log_files:
            file_date_str = log_file.split('_')[-1].replace('.txt', '')
            try:
                file_date = datetime.strptime(file_date_str, '%Y%m%d')
                if file_date < cutoff_date:
                    os.remove(log_file)
                    logging.info(f"Archivo antiguo eliminado: {log_file}")
            except:
                pass
        
        # Limpiar datasets diarios antiguos (más de 90 días)
        dataset_files = glob.glob('data/over_under_daily_*.csv')
        cutoff_date = datetime.now() - timedelta(days=90)
        
        for dataset_file in dataset_files:
            file_date_str = dataset_file.split('_')[-1].replace('.csv', '')
            try:
                file_date = datetime.strptime(file_date_str, '%Y%m%d')
                if file_date < cutoff_date:
                    os.remove(dataset_file)
                    logging.info(f"Dataset antiguo eliminado: {dataset_file}")
            except:
                pass
                
    except Exception as e:
        logging.warning(f"Error en limpieza de archivos: {e}")

if __name__ == "__main__":
    # Ejecutar limpieza
    cleanup_old_files()
    
    # Ejecutar re-entrenamiento
    exit_code = main()
    
    if exit_code == 0:
        print("✅ Re-entrenamiento completado exitosamente")
    else:
        print("❌ Error en re-entrenamiento")
    
    sys.exit(exit_code) 
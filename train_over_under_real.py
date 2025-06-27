#!/usr/bin/env python3
"""
Script para entrenar el modelo Over/Under con datos reales de MLB.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from over_under_model import OverUnderModel, create_over_under_dataset
import os

def collect_historical_data(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Recolecta datos históricos de Over/Under para entrenar el modelo.
    """
    print(f"Recolectando datos desde {start_date} hasta {end_date}...")
    
    all_data = []
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    while current_date <= end_date:
        fecha_str = current_date.strftime('%Y-%m-%d')
        print(f"Procesando fecha: {fecha_str}")
        
        try:
            dataset = create_over_under_dataset(fecha_str)
            if not dataset.empty:
                # Solo incluir juegos finalizados con total_runs válido
                dataset_clean = dataset.dropna(subset=['total_runs'])
                if not dataset_clean.empty:
                    all_data.append(dataset_clean)
                    print(f"  - {len(dataset_clean)} juegos válidos encontrados")
                else:
                    print(f"  - No hay juegos finalizados válidos")
            else:
                print(f"  - No hay datos disponibles")
        except Exception as e:
            print(f"  - Error procesando {fecha_str}: {e}")
        
        current_date += timedelta(days=1)
    
    if all_data:
        combined_data = pd.concat(all_data, ignore_index=True)
        print(f"\nTotal de juegos recolectados: {len(combined_data)}")
        return combined_data
    else:
        print("No se pudieron recolectar datos históricos")
        return pd.DataFrame()

def train_model_with_real_data():
    """
    Entrena el modelo Over/Under con datos reales.
    """
    print("=== Entrenamiento del Modelo Over/Under con Datos Reales ===\n")
    
    # Definir rango de fechas para entrenamiento (últimos 30 días)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Recolectar datos históricos
    historical_data = collect_historical_data(start_date, end_date)
    
    if historical_data.empty:
        print("No hay datos suficientes para entrenar. Usando datos simulados...")
        model = OverUnderModel()
        model._train_basic_model()
        return
    
    # Mostrar estadísticas de los datos
    print(f"\n=== Estadísticas de los Datos ===")
    print(f"Total de juegos: {len(historical_data)}")
    print(f"Promedio de carreras por juego: {historical_data['total_runs'].mean():.2f}")
    print(f"Desviación estándar: {historical_data['total_runs'].std():.2f}")
    print(f"Rango: {historical_data['total_runs'].min()} - {historical_data['total_runs'].max()}")
    
    # Verificar que tenemos todas las columnas necesarias
    required_columns = [
        'home_avg_runs', 'away_avg_runs', 'home_era', 'away_era',
        'home_whip', 'away_whip', 'temp_celsius', 'wind_kph', 'is_dome', 'total_runs'
    ]
    
    missing_columns = [col for col in required_columns if col not in historical_data.columns]
    if missing_columns:
        print(f"Columnas faltantes: {missing_columns}")
        print("Usando datos simulados como fallback...")
        model = OverUnderModel()
        model._train_basic_model()
        return
    
    # Entrenar el modelo
    print(f"\n=== Entrenando Modelo ===")
    model = OverUnderModel()
    
    try:
        result = model.fit_over_under_model(historical_data)
        
        if result['success']:
            print(f"✅ Modelo entrenado exitosamente!")
            print(f"MAE: {result['mae']:.2f}")
            print(f"RMSE: {result['rmse']:.2f}")
            print(f"\nImportancia de características:")
            for feature, importance in result['feature_importance'].items():
                print(f"  {feature}: {importance:.3f}")
        else:
            print(f"❌ Error entrenando modelo: {result.get('error', 'Desconocido')}")
            print("Usando datos simulados como fallback...")
            model._train_basic_model()
            
    except Exception as e:
        print(f"❌ Error durante el entrenamiento: {e}")
        print("Usando datos simulados como fallback...")
        model._train_basic_model()

if __name__ == "__main__":
    train_model_with_real_data() 
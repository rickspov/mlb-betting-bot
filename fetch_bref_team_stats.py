#!/usr/bin/env python3
"""
Script para descargar y guardar estadísticas de equipos MLB (bateo y pitcheo) de Baseball Reference para la temporada 2025.
"""
import pandas as pd
import datetime
import os

# URLs de Baseball Reference para 2025
BATTING_URL = "https://www.baseball-reference.com/leagues/MLB/2025-standard-batting.shtml"
PITCHING_URL = "https://www.baseball-reference.com/leagues/MLB/2025-standard-pitching.shtml"

OUTPUT_FILE = "data/bref_team_stats_2025.csv"


def fetch_bref_table(url: str, table_id: str) -> pd.DataFrame:
    """Descarga y procesa una tabla de Baseball Reference usando pandas.read_html."""
    print(f"Descargando datos de: {url}")
    tables = pd.read_html(url, attrs={"id": table_id})
    if not tables:
        raise ValueError(f"No se encontró la tabla {table_id} en la página.")
    df = tables[0]
    # Eliminar filas de totales y equipos no MLB
    df = df[~df['Tm'].isin(['Tm', 'League Average', 'Total'])]
    df = df[df['Tm'].str.len() <= 20]  # Filtrar nombres largos (no equipos)
    return df.reset_index(drop=True)


def main():
    print("=== Descargando estadísticas de equipos MLB 2025 de Baseball Reference ===\n")
    # Descargar tablas
    batting = fetch_bref_table(BATTING_URL, "teams_standard_batting")
    pitching = fetch_bref_table(PITCHING_URL, "teams_standard_pitching")

    # Unir por nombre de equipo
    merged = pd.merge(batting, pitching, on='Tm', suffixes=('_bat', '_pit'))

    # Agregar fecha de actualización
    merged['last_update'] = datetime.datetime.now().strftime('%Y-%m-%d')

    # Guardar CSV
    os.makedirs('data', exist_ok=True)
    merged.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Estadísticas guardadas en {OUTPUT_FILE}")
    print(f"Columnas disponibles: {list(merged.columns)}")

if __name__ == "__main__":
    main() 
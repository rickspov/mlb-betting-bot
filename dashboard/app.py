# app.py
# Dashboard mejorado para MLB Betting Bot usando Streamlit con tabs y diseño moderno.

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
from typing import Dict, List

# Importaciones locales
from data_manager.query import get_players_by_date
from data_manager.results import get_results_by_date
from dfs_optimizer.optimize_lineup import optimize_lineup
from analysis.compare_results import compare_lineup_vs_actual
from run_daily_optimizer import run_optimizer
from mlb_stats_integration import (
    obtener_partidos_con_probabilidades,
    obtener_alineaciones_confirmadas,
    obtener_datos_para_optimizacion,
    get_weather_and_stadium,
    update_daily_player_stats,
    get_match_real_stats
)
from over_under_model import over_under_model, create_over_under_dataset
import statsapi

# Configuración de la página
st.set_page_config(
    page_title="⚾ MLB Betting Bot Dashboard",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh cada 3 minutos
st_autorefresh(interval=180000, key="data_refresh")

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        color: #000000 !important;
    }
    .metric-card h4 {
        color: #000000 !important;
        margin-bottom: 0.5rem;
    }
    .metric-card p {
        color: #000000 !important;
        margin: 0.25rem 0;
    }
    .metric-card strong {
        color: #1f77b4 !important;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .success-card {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .warning-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Agregar estilos personalizados para tabs
st.markdown('''
    <style>
    /* Tabs personalizados para mejor contraste */
    .stTabs [data-baseweb="tab-list"] {
        background: #222831;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 0.5rem 0 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        color: #fff !important;
        background: #393e46 !important;
        border-radius: 8px 8px 0 0;
        margin-right: 0.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: background 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: #00adb5 !important;
        color: #fff !important;
    }
    .stTabs [aria-selected="false"] {
        opacity: 0.7;
    }
    </style>
''', unsafe_allow_html=True)

# Constantes
MIN_PLAYERS_REQUIRED = 7
JUGADORES_FILE = "data/manual_jugadores.csv"
RESULTADOS_FILE = "data/manual_resultados.csv"
OVER_UNDER_RESULTS_FILE = "data/over_under_results.csv"

@st.cache_data(ttl=300)  # Cache por 5 minutos
def obtener_juegos_del_dia(fecha_str: str) -> List[Dict]:
    """Obtiene juegos del día con cache."""
    try:
        juegos = statsapi.schedule(date=fecha_str)
        juegos_con_scores = []
        
        for j in juegos:
            juego_data = {
                'game_id': j['game_id'],
                'desc': f"{j['away_name']} @ {j['home_name']} - {j['game_datetime']} - {j['status']}",
                'home_name': j['home_name'],
                'away_name': j['away_name'],
                'status': j['status'],
                'game_datetime': j['game_datetime'],
                'home_score': j.get('home_score'),
                'away_score': j.get('away_score')
            }
            juegos_con_scores.append(juego_data)
        
        return juegos_con_scores
    except Exception as e:
        st.error(f"Error obteniendo juegos: {e}")
        return []

@st.cache_data(ttl=600)  # Cache por 10 minutos
def obtener_weather_info(game_id: str) -> Dict:
    """Obtiene información del clima y estadio."""
    return get_weather_and_stadium(game_id)

def mostrar_weather_card(weather_info: Dict):
    """Muestra información del clima en una card."""
    with st.container():
        st.markdown(f"""
        <div class="weather-card">
            <h4>🌤️ Clima & Estadio</h4>
            <p><strong>Estadio:</strong> {weather_info.get('stadium_name', 'N/A')}</p>
            <p><strong>Temperatura:</strong> {weather_info.get('temp_celsius', 'N/A')}°C</p>
            <p><strong>Viento:</strong> {weather_info.get('wind_kph', 'N/A')} km/h</p>
            <p><strong>Condiciones:</strong> {weather_info.get('conditions', 'N/A')}</p>
            <p><strong>Tipo:</strong> {'🏟️ Domed' if weather_info.get('is_dome') else '🌅 Open Air'}</p>
        </div>
        """, unsafe_allow_html=True)

def obtener_roster_estructurado(team_name: str) -> List[Dict]:
    """Obtiene roster estructurado de un equipo."""
    try:
        team_info = statsapi.lookup_team(team_name)
        if not team_info:
            return []
        team_id = team_info[0]['id']
        roster_data = statsapi.get('team_roster', {'teamId': team_id, 'rosterType': 'active'})
        jugadores = roster_data.get('roster', [])
        return jugadores
    except Exception as e:
        st.error(f"Error obteniendo roster para {team_name}: {e}")
        return []

def mostrar_roster_por_posiciones(team_name: str) -> List[Dict]:
    """Muestra roster organizado por posiciones (pitchers, outfield, infield)."""
    jugadores = obtener_roster_estructurado(team_name)
    if not jugadores:
        st.warning(f"No hay alineación confirmada para {team_name}.")
        return []
    
    # Categorizar jugadores por posición
    pitchers = []
    outfielders = []
    infielders = []
    others = []
    
    for jugador in jugadores:
        nombre = jugador.get('person', {}).get('fullName', '')
        posicion = jugador.get('position', {}).get('abbreviation', '')
        jersey = jugador.get('jerseyNumber', '')
        
        jugador_data = {
            'name': nombre,
            'team': team_name,
            'position': posicion,
            'jersey': jersey
        }
        
        # Categorizar por posición
        if posicion in ['P', 'SP', 'RP', 'CP']:
            pitchers.append(jugador_data)
        elif posicion in ['OF', 'LF', 'CF', 'RF']:
            outfielders.append(jugador_data)
        elif posicion in ['1B', '2B', '3B', 'SS', 'C']:
            infielders.append(jugador_data)
        else:
            others.append(jugador_data)
    
    # Mostrar por categorías
    st.markdown(f"**{team_name}**")
    
    if pitchers:
        st.markdown("**⚾ Pitchers:**")
        for p in pitchers:
            st.write(f"• {p['name']} ({p['position']} #{p['jersey']})")
        st.divider()
    
    if outfielders:
        st.markdown("**🏃 Outfielders:**")
        for of in outfielders:
            st.write(f"• {of['name']} ({of['position']} #{of['jersey']})")
        st.divider()
    
    if infielders:
        st.markdown("**🏠 Infielders:**")
        for inf in infielders:
            st.write(f"• {inf['name']} ({inf['position']} #{inf['jersey']})")
        st.divider()
    
    if others:
        st.markdown("**📋 Otros:**")
        for o in others:
            st.write(f"• {o['name']} ({o['position']} #{o['jersey']})")
        st.divider()
    
    # Retornar lista completa
    return pitchers + outfielders + infielders + others

def mostrar_roster_dashboard(team_name: str) -> List[Dict]:
    """Muestra roster en el dashboard."""
    jugadores = obtener_roster_estructurado(team_name)
    if not jugadores:
        st.warning(f"No hay alineación confirmada para {team_name}.")
        return []
    
    st.write(f"**Roster de {team_name}:**")
    roster_list = []
    for jugador in jugadores:
        nombre = jugador.get('person', {}).get('fullName', '')
        posicion = jugador.get('position', {}).get('abbreviation', '')
        jersey = jugador.get('jerseyNumber', '')
        st.write(f"{nombre} | {posicion} | #{jersey}")
        roster_list.append({
            'name': nombre,
            'team': team_name,
            'position': posicion,
            'jersey': jersey
        })
    return roster_list

def crear_over_under_heatmap(predictions: List[Dict]) -> go.Figure:
    """Crea heatmap para Over/Under predictions."""
    if not predictions:
        return None
    
    # Preparar datos para el heatmap
    teams = []
    linea_oficial = []
    linea_predicha = []
    resultado_real = []
    accuracy = []
    
    for pred in predictions:
        teams.append(f"{pred['away_team']} @ {pred['home_team']}")
        linea_oficial.append(pred.get('linea_oficial', 0))
        linea_predicha.append(pred.get('linea_predicha', 0))
        resultado_real.append(pred.get('resultado_real', 0))
        
        # Calcular accuracy (verde si acierta, rojo si falla)
        if pred.get('resultado_real') and pred.get('linea_oficial'):
            real = pred['resultado_real']
            oficial = pred['linea_oficial']
            if (real > oficial and pred.get('linea_predicha', 0) > oficial) or \
               (real < oficial and pred.get('linea_predicha', 0) < oficial):
                accuracy.append(1)  # Verde
            else:
                accuracy.append(0)  # Rojo
        else:
            accuracy.append(0.5)  # Gris
    
    # Crear heatmap
    fig = go.Figure(data=go.Heatmap(
        z=[linea_oficial, linea_predicha, resultado_real],
        x=teams,
        y=['Línea Oficial', 'Línea Predicha', 'Resultado Real'],
        colorscale='RdYlGn',
        text=[[f"{val:.1f}" if val else "N/A" for val in linea_oficial],
              [f"{val:.1f}" if val else "N/A" for val in linea_predicha],
              [f"{val:.1f}" if val else "N/A" for val in resultado_real]],
        texttemplate="%{text}",
        textfont={"size": 12},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Heatmap Over/Under: Oficial vs Predicción vs Realidad",
        xaxis_title="Juegos",
        yaxis_title="Métricas",
        height=400
    )
    
    return fig

def guardar_over_under_result(result_data: Dict):
    """Guarda resultado Over/Under en CSV."""
    try:
        df = pd.DataFrame([result_data])
        if os.path.exists(OVER_UNDER_RESULTS_FILE):
            df.to_csv(OVER_UNDER_RESULTS_FILE, mode='a', header=False, index=False)
        else:
            df.to_csv(OVER_UNDER_RESULTS_FILE, index=False)
        st.success("Resultado Over/Under guardado exitosamente.")
    except Exception as e:
        st.error(f"Error guardando resultado: {e}")

def cargar_over_under_historico() -> pd.DataFrame:
    """Carga histórico de resultados Over/Under."""
    try:
        if os.path.exists(OVER_UNDER_RESULTS_FILE):
            return pd.read_csv(OVER_UNDER_RESULTS_FILE)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error cargando histórico: {e}")
        return pd.DataFrame()

def tab_juegos_del_dia(fecha_str: str):
    """Tab para mostrar juegos del día con clima y Over/Under."""
    st.header("🏟️ Juegos del Día")
    
    juegos = obtener_juegos_del_dia(fecha_str)
    if not juegos:
        st.info("No hay juegos para esta fecha.")
        return
    
    # Crear dataset para Over/Under predictions
    juegos_df = pd.DataFrame(juegos)
    if not juegos_df.empty:
        # Obtener predicciones Over/Under
        predictions = over_under_model.predict_over_under(juegos_df)
    else:
        predictions = []
    
    # Mostrar cada juego
    for i, juego in enumerate(juegos):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(juego)  # DEPURACIÓN: Ver los datos del juego en el dashboard
                # Mostrar score final si el partido está finalizado
                score_info = ""
                if juego['status'] == 'Final' and juego.get('home_score') is not None and juego.get('away_score') is not None:
                    score_info = f"<p><strong>🏆 Score Final:</strong> {juego['away_name']} {juego['away_score']} - {juego['home_score']} {juego['home_name']}</p>"
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{juego['away_name']} @ {juego['home_name']}</h4>
                    <p><strong>Estado:</strong> {juego['status']}</p>
                    <p><strong>Hora:</strong> {juego['game_datetime']}</p>
                    {score_info}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if i < len(predictions):
                    pred = predictions[i]
                    if pred.get('linea_predicha'):
                        st.metric(
                            "Over/Under Predicho",
                            f"{pred['linea_predicha']:.1f}",
                            f"Conf: {pred['confidence']:.1%}"
                        )
            
            # Mostrar clima
            weather_info = obtener_weather_info(juego['game_id'])
            mostrar_weather_card(weather_info)
            
            st.divider()

def tab_optimizacion_dfs(fecha_str: str):
    """Tab para optimización DFS."""
    st.header("🎯 Optimización DFS")
    
    # Selección de juego
    juegos = obtener_juegos_del_dia(fecha_str)
    if not juegos:
        st.info("No hay juegos para esta fecha.")
        return
    
    juego_seleccionado = st.selectbox(
        "Selecciona un juego",
        juegos,
        format_func=lambda x: x['desc']
    )
    
    if juego_seleccionado:
        game_id = juego_seleccionado['game_id']
        equipos = [juego_seleccionado['home_name'], juego_seleccionado['away_name']]
        
        # Mostrar clima del juego seleccionado
        weather_info = obtener_weather_info(game_id)
        mostrar_weather_card(weather_info)
        
        # Construir roster
        st.subheader("📋 Rosters Confirmados")
        
        # Mostrar rosters lado a lado organizados por posiciones
        col1, col2 = st.columns(2)
        
        roster = []
        for i, equipo in enumerate(equipos):
            with col1 if i == 0 else col2:
                equipo_roster = mostrar_roster_por_posiciones(equipo)
                roster.extend(equipo_roster)
        
        if not roster:
            st.warning("No se pudo obtener el roster para este juego.")
            return
        
        # Formulario para FPPG y precio
        st.subheader("💰 Ingresa FPPG y Precio FanDuel")
        input_data = []
        
        with st.form("fppg_precio_form"):
            st.write("**Completa los datos para cada jugador:**")
            
            # Separar jugadores por equipo y filtrar solo bateadores (no pitchers)
            bateadores_home = [j for j in roster if j.get('team') == equipos[0] and j.get('position') not in ['P', 'SP', 'RP', 'CP']]
            bateadores_away = [j for j in roster if j.get('team') == equipos[1] and j.get('position') not in ['P', 'SP', 'RP', 'CP']]
            
            # Crear dos columnas para los equipos
            col_home, col_away = st.columns(2)
            
            # Equipo Home (columna izquierda)
            with col_home:
                st.markdown(f"**{equipos[0]}**")
                for jugador in bateadores_home:
                    nombre = jugador.get('name', '')
                    posicion = jugador.get('position', '')
                    jersey = jugador.get('jersey', '')
                    
                    st.write(f"**{nombre}** ({posicion} #{jersey})")
                    
                    # Checkbox para marcar como activo/inactivo
                    activo = st.checkbox("Activo", value=True, key=f"activo_{nombre}")
                    
                    if activo:
                        cols = st.columns([1, 1])
                        fppg = cols[0].number_input(f"FPPG", min_value=0.0, key=f"fppg_{nombre}")
                        precio = cols[1].number_input(f"Precio", min_value=0, key=f"precio_{nombre}")
                        
                        jugador_copia = jugador.copy()
                        jugador_copia['fppg'] = fppg
                        jugador_copia['salary'] = precio
                        jugador_copia['activo'] = True
                        input_data.append(jugador_copia)
                    else:
                        st.info("Jugador marcado como inactivo - será excluido de la optimización")
                        jugador_copia = jugador.copy()
                        jugador_copia['activo'] = False
                        input_data.append(jugador_copia)
                    
                    st.divider()
            
            # Equipo Away (columna derecha)
            with col_away:
                st.markdown(f"**{equipos[1]}**")
                for jugador in bateadores_away:
                    nombre = jugador.get('name', '')
                    posicion = jugador.get('position', '')
                    jersey = jugador.get('jersey', '')
                    
                    st.write(f"**{nombre}** ({posicion} #{jersey})")
                    
                    # Checkbox para marcar como activo/inactivo
                    activo = st.checkbox("Activo", value=True, key=f"activo_{nombre}")
                    
                    if activo:
                        cols = st.columns([1, 1])
                        fppg = cols[0].number_input(f"FPPG", min_value=0.0, key=f"fppg_{nombre}")
                        precio = cols[1].number_input(f"Precio", min_value=0, key=f"precio_{nombre}")
                        
                        jugador_copia = jugador.copy()
                        jugador_copia['fppg'] = fppg
                        jugador_copia['salary'] = precio
                        jugador_copia['activo'] = True
                        input_data.append(jugador_copia)
                    else:
                        st.info("Jugador marcado como inactivo - será excluido de la optimización")
                        jugador_copia = jugador.copy()
                        jugador_copia['activo'] = False
                        input_data.append(jugador_copia)
                    
                    st.divider()
            
            submitted = st.form_submit_button("🚀 Optimizar Alineación")
        
        # Optimización
        if submitted:
            # Filtrar solo jugadores activos
            jugadores_activos = [j for j in input_data if j.get('activo', True)]
            
            if len(jugadores_activos) < MIN_PLAYERS_REQUIRED:
                st.error(f"Se requieren al menos {MIN_PLAYERS_REQUIRED} jugadores activos para optimizar. Tienes {len(jugadores_activos)}.")
            # Solo validar FPPG y precio de los jugadores activos
            elif any(j.get('activo', True) and (j.get('fppg', 0) <= 0 or j.get('salary', 0) <= 0) for j in jugadores_activos):
                st.error("Todos los jugadores activos deben tener FPPG y precio válidos.")
            else:
                # Debug: mostrar los datos de entrada al optimizador
                st.subheader("🛠️ Debug: Jugadores activos enviados al optimizador")
                st.code(str(jugadores_activos), language='python')
                with st.spinner("Optimizando alineación..."):
                    resultado = run_optimizer(players_data=jugadores_activos)
                
                if resultado.get('status') == 'success':
                    st.markdown("""
                    <div class="success-card">
                        <h3>✅ ¡Alineación Óptima Generada!</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Mostrar MVP
                    mvp = resultado.get('mvp', {})
                    col1, col2, col3 = st.columns(3)
                    col1.metric("🏆 MVP", mvp.get('name', ''), f"${mvp.get('salary', 0)}")
                    col2.metric("FPPG MVP", f"{mvp.get('fppg', 0):.2f}")
                    col3.metric("Puntos Proyectados", f"{resultado.get('projected_points', 0):.2f}")
                    
                    # Mostrar utilities
                    st.subheader("👥 Alineación Completa (Utilities)")
                    utility = resultado.get('utility', [])
                    if not utility:
                        st.warning("No se pudo armar la alineación óptima. Es posible que el presupuesto de $60,000 sea insuficiente para los salarios ingresados. Prueba bajando los salarios o revisa los datos.")
                        # Mostrar MVP y 5 utilities más baratos posibles
                        jugadores_ordenados = sorted(jugadores_activos, key=lambda x: x['salary'])
                        mvp_barato = min(jugadores_activos, key=lambda x: x['salary'])
                        utilities_baratos = [j for j in jugadores_ordenados if j != mvp_barato][:5]
                        total_salario = int(mvp_barato['salary'] * 1.5 + sum(j['salary'] for j in utilities_baratos))
                        st.info(f"Ejemplo: MVP más barato ({mvp_barato['name']}, ${mvp_barato['salary']} x1.5) + 5 utilities más baratos suma: ${total_salario}")
                        data_tabla = [
                            {"Rol": "MVP (más barato)", **mvp_barato, "Salario Ajustado": int(mvp_barato['salary']*1.5)}
                        ] + [
                            {"Rol": f"Utility {i+1}", **j, "Salario Ajustado": j['salary']} for i, j in enumerate(utilities_baratos)
                        ]
                        st.table(data_tabla)
                    for i, jugador in enumerate(utility, 1):
                        if isinstance(jugador, dict):
                            st.write(f"{i}. {jugador.get('name', '')} | ${jugador.get('salary', 0)} | FPPG: {jugador.get('fppg', 0)}")
                        else:
                            st.write(f"{i}. {jugador}")
                    
                    # Debug: mostrar el contenido de utilities en bruto
                    st.code(str(utility), language='python')
                    
                    # Métricas finales
                    col1, col2 = st.columns(2)
                    col1.metric("💰 Salario Total", f"${resultado.get('salary_used', 0)}")
                    col2.metric("📊 Puntos Proyectados", f"{resultado.get('projected_points', 0):.2f}")
                    
                    # Guardar datos
                    os.makedirs("data/opt_inputs", exist_ok=True)
                    file = f"data/opt_inputs/opt_inputs_{fecha_str}_{game_id}.csv"
                    pd.DataFrame(input_data).to_csv(file, index=False)
                    st.info(f"Datos guardados en: {file}")

                    # --- What if: Mejor alineación para cada posible MVP ---
                    st.subheader("🔎 What if: Mejor alineación posible para cada MVP")
                    whatif_rows = []
                    for posible_mvp in jugadores_activos:
                        # MVP fijo
                        mvp_salario = posible_mvp['salary'] * 1.5
                        mvp_fppg = posible_mvp['fppg'] * 1.5
                        # Utilities candidatos (sin el MVP)
                        candidates = [j for j in jugadores_activos if j != posible_mvp]
                        # Ordenar por FPPG/Precio descendente (mejor valor)
                        candidates = sorted(candidates, key=lambda x: (x['fppg']/x['salary'] if x['salary'] > 0 else 0), reverse=True)
                        # Probar todas las combinaciones de 5 utilities
                        from itertools import combinations
                        best_utilities = []
                        best_fppg = 0
                        best_salary = 0
                        for combo in combinations(candidates, 5):
                            total_salary = mvp_salario + sum(j['salary'] for j in combo)
                            if total_salary <= 60000:
                                total_fppg = mvp_fppg + sum(j['fppg'] for j in combo)
                                if total_fppg > best_fppg:
                                    best_fppg = total_fppg
                                    best_salary = total_salary
                                    best_utilities = combo
                        if best_utilities:
                            whatif_rows.append({
                                'MVP': posible_mvp['name'],
                                'FPPG MVP': round(posible_mvp['fppg'],2),
                                'Salario MVP (x1.5)': int(mvp_salario),
                                'Utilities': ', '.join(j['name'] for j in best_utilities),
                                'FPPG Total': round(best_fppg,2),
                                'Salario Total': int(best_salary)
                            })
                    if whatif_rows:
                        st.dataframe(whatif_rows, use_container_width=True)
                    else:
                        st.info("No hay combinaciones posibles para ningún MVP bajo el presupuesto actual.")
                else:
                    st.error(f"Error en optimización: {resultado.get('message', 'Desconocido')}")

def tab_over_under(fecha_str: str):
    """Tab para Over/Under predictions y heatmap."""
    st.header("📊 Over/Under Analysis")
    
    # Obtener predicciones para el día
    juegos = obtener_juegos_del_dia(fecha_str)
    if not juegos:
        st.info("No hay juegos para esta fecha.")
        return
    
    # Construir features reales para cada juego
    features = []
    for juego in juegos:
        try:
            match_stats = get_match_real_stats(juego)
            features.append({
                'game_id': juego['game_id'],
                'home_team': juego['home_name'],
                'away_team': juego['away_name'],
                **{k: match_stats[k] for k in [
                    'home_avg_runs', 'away_avg_runs', 'home_era', 'away_era',
                    'home_whip', 'away_whip'
                ]}
            })
        except Exception as e:
            print(f'Error obteniendo stats para {juego}: {e}')
    juegos_df = pd.DataFrame(features)
    predictions = over_under_model.predict_over_under(juegos_df) if not juegos_df.empty else []

    # Mostrar predicciones
    if predictions:
        st.subheader("🎯 Predicciones Over/Under")
        for pred in predictions:
            if pred.get('linea_predicha'):
                col1, col2, col3, col4 = st.columns(4)
                col1.write(f"**{pred['away_team']} @ {pred['home_team']}**")
                col2.metric("Línea Oficial", f"{pred.get('linea_oficial', 'N/A')}")
                col3.metric("Línea Predicha", f"{pred['linea_predicha']:.1f}")
                col4.metric("Confianza", f"{pred['confidence']:.1%}")
        # Heatmap
        st.subheader("🔥 Heatmap Comparativo")
        fig = crear_over_under_heatmap(predictions)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    # Formulario para ingresar resultados reales
    st.subheader("📝 Ingresa Resultados Reales")
    with st.form("over_under_results_form"):
        st.write("Ingresa los resultados reales de los juegos:")
        
        for pred in predictions:
            game_desc = f"{pred['away_team']} @ {pred['home_team']}"
            resultado_real = st.number_input(
                f"Total carreras - {game_desc}",
                min_value=0,
                key=f"resultado_{pred['game_id']}"
            )
            pred['resultado_real'] = resultado_real
        
        submitted = st.form_submit_button("💾 Guardar Resultados")
        
        if submitted:
            for pred in predictions:
                if pred.get('resultado_real', 0) > 0:
                    result_data = {
                        'date': fecha_str,
                        'game_id': pred['game_id'],
                        'away_team': pred['away_team'],
                        'home_team': pred['home_team'],
                        'linea_oficial': pred.get('linea_oficial'),
                        'linea_predicha': pred.get('linea_predicha'),
                        'resultado_real': pred.get('resultado_real'),
                        'accuracy': 1 if pred.get('resultado_real') and pred.get('linea_oficial') and \
                                    ((pred['resultado_real'] > pred['linea_oficial'] and pred.get('linea_predicha', 0) > pred['linea_oficial']) or \
                                     (pred['resultado_real'] < pred['linea_oficial'] and pred.get('linea_predicha', 0) < pred['linea_oficial'])) else 0
                    }
                    guardar_over_under_result(result_data)

def tab_resultados_reales():
    """Tab para resultados reales e histórico."""
    st.header("📈 Resultados Reales & Histórico")
    
    # Cargar histórico
    historico = cargar_over_under_historico()
    
    if not historico.empty:
        st.subheader("📊 Histórico de Resultados")
        
        # Métricas generales
        total_games = len(historico)
        accuracy_rate = historico['accuracy'].mean() * 100 if 'accuracy' in historico.columns else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Juegos", total_games)
        col2.metric("Tasa de Acierto", f"{accuracy_rate:.1f}%")
        col3.metric("Última Actualización", historico['date'].max() if 'date' in historico.columns else "N/A")
        
        # Tabla de resultados
        st.dataframe(historico, use_container_width=True)
        
        # Gráfico de accuracy por fecha
        if 'date' in historico.columns and 'accuracy' in historico.columns:
            st.subheader("📈 Tasa de Acierto por Fecha")
            accuracy_by_date = historico.groupby('date')['accuracy'].mean().reset_index()
            fig = px.line(accuracy_by_date, x='date', y='accuracy', 
                         title="Evolución de la Tasa de Acierto")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos históricos disponibles. Ingresa resultados en la pestaña Over/Under.")

def main_dashboard():
    """Función principal del dashboard."""
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>⚾ MLB Betting Bot Dashboard</h1>
        <p>Optimización DFS • Over/Under • Análisis en Tiempo Real</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Selección de fecha
        selected_date = st.date_input(
            "📅 Selecciona la fecha",
            value=date.today(),
            max_value=date.today() + timedelta(days=7)
        )
        fecha_str = selected_date.strftime('%Y-%m-%d')
        
        st.write(f"**Fecha seleccionada:** {fecha_str}")
        
        # Botón para actualizar stats
        if st.button("🔄 Actualizar Stats Diarios"):
            with st.spinner("Actualizando stats..."):
                stats_file = update_daily_player_stats(fecha_str)
                if stats_file:
                    st.success(f"Stats actualizados: {stats_file}")
                else:
                    st.warning("No se pudieron actualizar stats")
        
        # Información del sistema
        st.markdown("---")
        st.subheader("ℹ️ Información")
        st.write("• Auto-refresh cada 3 minutos")
        st.write("• Cache de datos activo")
        st.write("• Modelo Over/Under entrenado")
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏟️ Juegos del Día",
        "🎯 Optimización DFS", 
        "📊 Over/Under",
        "📈 Resultados Reales"
    ])
    
    with tab1:
        tab_juegos_del_dia(fecha_str)
    
    with tab2:
        tab_optimizacion_dfs(fecha_str)
    
    with tab3:
        tab_over_under(fecha_str)
    
    with tab4:
        tab_resultados_reales()

if __name__ == "__main__":
    main_dashboard() 
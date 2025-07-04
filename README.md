# ⚾ MLB Betting Bot Dashboard

Sistema integral de análisis y optimización para apuestas de MLB, incluyendo optimización DFS, predicciones Over/Under, y análisis en tiempo real.

## 🚀 Características Principales

- **🏟️ Juegos del Día**: Visualización de partidos con clima y estadio
- **🎯 Optimización DFS**: Generación de alineaciones óptimas para FanDuel
- **📊 Over/Under Analysis**: Predicciones con modelo ML y heatmaps comparativos
- **📈 Resultados Reales**: Seguimiento histórico y métricas de rendimiento
- **🌤️ Clima & Estadio**: Información meteorológica y características del venue
- **🔄 Auto-refresh**: Actualización automática cada 3 minutos

## 📋 Requisitos

- Python 3.8+
- pip
- Conexión a internet (para MLB-StatsAPI)

## 🛠️ Instalación

1. **Clonar el repositorio:**
```bash
git clone <repository-url>
cd MLBBETTINGBOT
```

2. **Crear entorno virtual:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Instalar dependencias adicionales:**
```bash
pip install streamlit-autorefresh plotly
```

## 🏃‍♂️ Cómo Ejecutar el Dashboard

### Opción 1: Ejecución Directa
```bash
cd dashboard
streamlit run app.py
```

### Opción 2: Con Puerto Específico
```bash
streamlit run app.py --server.port 8501
```

### Opción 3: Modo Desarrollo
```bash
streamlit run app.py --server.runOnSave true
```

El dashboard estará disponible en: `http://localhost:8501`

## 📊 Workflow Diario

### 1. **Preparación Matutina**
- Abrir el dashboard
- Seleccionar fecha del día
- Revisar juegos programados en la pestaña "Juegos del Día"
- Verificar clima y estadios

### 2. **Análisis Over/Under**
- Ir a pestaña "Over/Under"
- Revisar predicciones del modelo
- Analizar heatmap comparativo
- Tomar decisiones de apuestas

### 3. **Optimización DFS**
- Ir a pestaña "Optimización DFS"
- Seleccionar juego específico
- Revisar rosters confirmados
- Ingresar FPPG y precios FanDuel
- Generar alineación óptima

### 4. **Seguimiento de Resultados**
- Después de los juegos, ir a pestaña "Over/Under"
- Ingresar resultados reales
- Verificar accuracy del modelo
- Revisar histórico en pestaña "Resultados Reales"

### 5. **Mantenimiento Nocturno**
- Ejecutar script de re-entrenamiento:
```bash
python automations/retrain_over_under_daily.py
```

## 🔧 Configuración Automática

### Re-entrenamiento Diario (Opcional)

Para configurar re-entrenamiento automático cada noche:

**Windows (Task Scheduler):**
```bash
# Crear tarea programada para ejecutar a las 2:00 AM
schtasks /create /tn "MLB_Retrain" /tr "python automations/retrain_over_under_daily.py" /sc daily /st 02:00
```

**Linux/macOS (Crontab):**
```bash
# Agregar a crontab (ejecutar a las 2:00 AM)
0 2 * * * cd /path/to/MLBBETTINGBOT && python automations/retrain_over_under_daily.py
```

## 📁 Estructura del Proyecto

```
MLBBETTINGBOT/
├── dashboard/
│   └── app.py                 # Dashboard principal
├── mlb_stats_integration.py   # Integración con MLB-StatsAPI
├── over_under_model.py        # Modelo Over/Under
├── automations/
│   └── retrain_over_under_daily.py  # Script de re-entrenamiento
├── data/
│   ├── opt_inputs/            # Datos de entrada para optimización
│   ├── player_stats_daily_*.csv  # Stats diarios de jugadores
│   └── over_under_results.csv # Resultados históricos
├── models/
│   └── over_under_model.pkl   # Modelo entrenado
└── requirements.txt
```

## 🎯 Funcionalidades por Pestaña

### 🏟️ Juegos del Día
- Lista de partidos del día seleccionado
- Información de clima y estadio
- Estado de los juegos (Pre-Game, Live, Final)
- Predicciones Over/Under preliminares

### 🎯 Optimización DFS
- Selección de juego específico
- Rosters confirmados de ambos equipos
- Formulario para FPPG y precios FanDuel
- Generación de alineación óptima
- Métricas de rendimiento proyectado

### 📊 Over/Under
- Predicciones del modelo ML
- Comparación línea oficial vs predicha
- Heatmap visual comparativo
- Formulario para ingresar resultados reales
- Indicadores de confianza

### 📈 Resultados Reales
- Histórico de resultados
- Métricas de accuracy del modelo
- Gráficos de evolución temporal
- Análisis de rendimiento

## 🔍 Troubleshooting

### Error de Conexión a MLB-StatsAPI
```bash
# Verificar conexión
python -c "import statsapi; print(statsapi.schedule(date='2024-01-01'))"
```

### Error de Dependencias
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

### Error de Puerto Ocupado
```bash
# Usar puerto alternativo
streamlit run app.py --server.port 8502
```

### Error de Cache
```bash
# Limpiar cache de Streamlit
streamlit cache clear
```

## 📈 Métricas y KPIs

- **Accuracy Over/Under**: Tasa de acierto del modelo
- **ROI DFS**: Retorno de inversión en optimizaciones
- **Tiempo de Respuesta**: Velocidad de generación de alineaciones
- **Uptime**: Disponibilidad del sistema

## 🔮 Próximas Mejoras

- [ ] Integración con más casas de apuestas
- [ ] Modelos ML avanzados (XGBoost, Neural Networks)
- [ ] Alertas en tiempo real
- [ ] API REST para integración externa
- [ ] Mobile app
- [ ] Análisis de tendencias avanzado

## 📞 Soporte

Para reportar bugs o solicitar features:
1. Crear issue en el repositorio
2. Incluir logs de error si aplica
3. Especificar versión de Python y dependencias

## 📄 Licencia

Este proyecto es para uso educativo y de investigación. No garantiza ganancias en apuestas deportivas.

---

**⚠️ Disclaimer**: Las apuestas deportivas conllevan riesgo de pérdida. Este sistema es una herramienta de análisis, no garantiza resultados positivos.

## 👨‍💻 Sección exclusiva para Héctor (v0.5)

¡Hola Héctor! Esta sección es para ti, para que puedas instalar y ejecutar el MLB Betting Bot en tu laptop con Windows, aunque no tengas experiencia previa con programación. Sigue estos pasos uno a uno:

### 1. Instalar Python
- Ve a [python.org/downloads](https://www.python.org/downloads/windows/)
- Descarga la última versión de Python 3.x para Windows.
- Ejecuta el instalador y **asegúrate de marcar la casilla "Add Python to PATH"** antes de hacer clic en "Install Now".

### 2. Instalar Git
- Ve a [git-scm.com/download/win](https://git-scm.com/download/win)
- Descarga el instalador de Git para Windows y ejecútalo.
- Durante la instalación, puedes dejar todas las opciones por defecto y hacer clic en "Next" hasta finalizar.

### 3. Descargar el proyecto
- Haz clic derecho en el escritorio y selecciona "Git Bash Here" (o abre la app "Git Bash" desde el menú de inicio).
- Escribe este comando y presiona Enter:
  ```bash
  git clone https://github.com/TU_USUARIO/TU_REPO.git
  ```
  (Reemplaza la URL por la de tu repositorio real si es diferente)
- Entra a la carpeta del proyecto:
  ```bash
  cd MLBBETTINGBOT
  ```

### 4. Instalar las dependencias
- Escribe este comando y presiona Enter:
  ```bash
  pip install -r requirements.txt
  ```
  (Esto instalará todo lo necesario para que funcione el programa)

### 5. Ejecutar el dashboard
- Ejecuta este comando:
  ```bash
  streamlit run dashboard/app.py
  ```
- Se abrirá una ventana en tu navegador con la app. Si no se abre, copia la dirección que aparece en la terminal (por ejemplo, `http://localhost:8501`) y pégala en tu navegador.

### 6. Notas importantes
- Si ves algún error, copia el mensaje y avísale a tu hijo para que te ayude.
- Para actualizar el programa, abre Git Bash en la carpeta del proyecto y ejecuta:
  ```bash
  git pull
  ```
- Si necesitas cerrar la app, simplemente cierra la ventana de la terminal o presiona `Ctrl+C` en la terminal.

### 7. Ejecutar y actualizar la app con un solo clic (opcional)

Para facilitarte el uso, tienes dos archivos especiales:

- **actualizar_app_hector.bat**: Actualiza la app y las dependencias automáticamente.
- **ejecutar_dashboard_hector.bat**: Ejecuta el dashboard de la app.

#### ¿Cómo usarlos?
1. Haz doble clic en `actualizar_app_hector.bat` para actualizar el programa antes de usarlo.
2. Haz doble clic en `ejecutar_dashboard_hector.bat` para abrir la app en tu navegador.

¡Así no necesitas escribir comandos manualmente! Si ves algún error, copia el mensaje y avísale a tu hijo.

---

¡Listo Héctor! Así podrás probar la app sin necesidad de saber programar. ¡Gracias por ayudar a testear la versión 0.5! ⚾

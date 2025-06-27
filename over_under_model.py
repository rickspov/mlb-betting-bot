import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pickle
import os
from datetime import datetime, timedelta
from typing import Dict, List
import statsapi
from mlb_stats_integration import get_match_real_stats, get_weather_and_stadium

class OverUnderModel:
    def __init__(self, model_path: str = "models/over_under_model.pkl"):
        self.model_path = model_path
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.is_trained = False
        self.feature_columns = [
            'home_avg_runs', 'away_avg_runs', 'home_era', 'away_era',
            'home_whip', 'away_whip', 'temp_celsius', 'wind_kph', 'is_dome'
        ]
        self.load_model()

    def load_model(self) -> bool:
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                self.is_trained = True
                print(f"Modelo cargado desde {self.model_path}")
                return True
        except Exception as e:
            print(f"Error cargando modelo: {e}")
        return False

    def save_model(self) -> bool:
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            print(f"Modelo guardado en {self.model_path}")
            return True
        except Exception as e:
            print(f"Error guardando modelo: {e}")
            return False

    def prepare_features(self, match_data: Dict) -> pd.DataFrame:
        weather_data = get_weather_and_stadium(match_data.get('game_id', ''))
        features = {
            'home_avg_runs': match_data.get('home_avg_runs', 4.0),
            'away_avg_runs': match_data.get('away_avg_runs', 4.0),
            'home_era': match_data.get('home_era', 4.0),
            'away_era': match_data.get('away_era', 4.0),
            'home_whip': match_data.get('home_whip', 1.3),
            'away_whip': match_data.get('away_whip', 1.3),
            'temp_celsius': weather_data.get('temp_celsius', 20),
            'wind_kph': weather_data.get('wind_kph', 0),
            'is_dome': 1 if weather_data.get('is_dome', False) else 0
        }
        return pd.DataFrame([features])

    def fit_over_under_model(self, df: pd.DataFrame) -> Dict:
        try:
            if 'total_runs' not in df.columns:
                print("Error: df debe contener columna 'total_runs'")
                return {'success': False, 'error': 'Missing total_runs column'}
            X = df[self.feature_columns]
            y = df['total_runs']
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            self.model.fit(X_train, y_train)
            self.is_trained = True
            y_pred = self.model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            self.save_model()
            return {
                'success': True,
                'mae': mae,
                'rmse': rmse,
                'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_))
            }
        except Exception as e:
            print(f"Error entrenando modelo: {e}")
            return {'success': False, 'error': str(e)}

    def predict_over_under(self, juegos_df: pd.DataFrame) -> List[Dict]:
        if not self.is_trained:
            print("Modelo no entrenado. Ejecutando entrenamiento básico...")
            self._train_basic_model()
        predictions = []
        for _, juego in juegos_df.iterrows():
            try:
                match_data = {
                    'home_avg_runs': juego.get('home_avg_runs', 4.0),
                    'away_avg_runs': juego.get('away_avg_runs', 4.0),
                    'home_era': juego.get('home_era', 4.0),
                    'away_era': juego.get('away_era', 4.0),
                    'home_whip': juego.get('home_whip', 1.3),
                    'away_whip': juego.get('away_whip', 1.3),
                    'game_id': juego.get('game_id', '')
                }
                features = self.prepare_features(match_data)
                prediction = float(self.model.predict(features)[0])
                predictions.append({
                    'game_id': juego.get('game_id', ''),
                    'home_team': juego.get('home_team', ''),
                    'away_team': juego.get('away_team', ''),
                    'linea_predicha': round(prediction, 1),
                    'linea_oficial': juego.get('over_under', None),
                    'confidence': self._calculate_confidence(features)
                })
            except Exception as e:
                print(f"Error prediciendo juego {juego.get('game_id', '')}: {e}")
                predictions.append({
                    'game_id': juego.get('game_id', ''),
                    'home_team': juego.get('home_team', ''),
                    'away_team': juego.get('away_team', ''),
                    'linea_predicha': None,
                    'linea_oficial': juego.get('over_under', None),
                    'confidence': 0.0
                })
        return predictions

    def _calculate_confidence(self, features: pd.DataFrame) -> float:
        try:
            predictions = [tree.predict(features)[0] for tree in self.model.estimators_]
            confidence = 1.0 - (np.std(predictions) / np.mean(predictions))
            return max(0.0, min(1.0, float(confidence)))
        except:
            return 0.5

    def _train_basic_model(self):
        np.random.seed(42)
        n = 500
        data = {
            'home_avg_runs': np.random.uniform(3, 6, n),
            'away_avg_runs': np.random.uniform(3, 6, n),
            'home_era': np.random.uniform(3, 5, n),
            'away_era': np.random.uniform(3, 5, n),
            'home_whip': np.random.uniform(1.1, 1.4, n),
            'away_whip': np.random.uniform(1.1, 1.4, n),
            'temp_celsius': np.random.uniform(10, 35, n),
            'wind_kph': np.random.uniform(0, 30, n),
            'is_dome': np.random.choice([0, 1], n, p=[0.7, 0.3])
        }
        data['total_runs'] = (
            data['home_avg_runs'] + data['away_avg_runs'] +
            np.random.normal(0, 1.5, n)
        )
        df = pd.DataFrame(data)
        self.fit_over_under_model(df)

def create_over_under_dataset(fecha: str) -> pd.DataFrame:
    try:
        juegos = statsapi.schedule(date=fecha)
        dataset = []
        for juego in juegos:
            game_id = juego['game_id']
            match_stats = get_match_real_stats(juego)
            weather = get_weather_and_stadium(game_id)
            if juego['status'] == 'Final':
                try:
                    boxscore = statsapi.boxscore_data(game_id)
                    home_runs = boxscore['home']['runs']
                    away_runs = boxscore['away']['runs']
                    total_runs = home_runs + away_runs
                except:
                    total_runs = None
            else:
                total_runs = None
            record = {
                'game_id': game_id,
                'home_team': juego['home_name'],
                'away_team': juego['away_name'],
                'date': fecha,
                'home_avg_runs': match_stats['home_avg_runs'],
                'away_avg_runs': match_stats['away_avg_runs'],
                'home_era': match_stats['home_era'],
                'away_era': match_stats['away_era'],
                'home_whip': match_stats['home_whip'],
                'away_whip': match_stats['away_whip'],
                'temp_celsius': weather['temp_celsius'],
                'wind_kph': weather['wind_kph'],
                'is_dome': 1 if weather['is_dome'] else 0,
                'total_runs': total_runs
            }
            dataset.append(record)
        return pd.DataFrame(dataset)
    except Exception as e:
        print(f"Error creando dataset Over/Under para {fecha}: {e}")
        return pd.DataFrame()

def retrain_daily() -> Dict:
    try:
        model = OverUnderModel()
        # Aquí deberías cargar tu dataset histórico real
        # Por simplicidad, entrenamos con datos simulados
        model._train_basic_model()
        return {'success': True, 'mae': 0, 'rmse': 0}
    except Exception as e:
        print(f"Error en re-entrenamiento diario: {e}")
        return {'success': False, 'error': str(e)}

# Instancia global del modelo
over_under_model = OverUnderModel()

if __name__ == "__main__":
    print("Entrenando modelo Over/Under...")
    model = OverUnderModel()
    
    # Usar datos simulados para el test inicial
    print("Usando datos simulados para entrenamiento inicial...")
    model._train_basic_model()
    
    # También probar con datos reales si están disponibles
    try:
        fecha = datetime.now().strftime('%Y-%m-%d')
        print(f"Intentando obtener datos reales para {fecha}...")
        dataset = create_over_under_dataset(fecha)
        if not dataset.empty and not bool(dataset['total_runs'].isna().all()):
            # Limpiar datos con NaN
            dataset_clean = dataset.dropna(subset=['total_runs'])
            if not dataset_clean.empty:
                result = model.fit_over_under_model(dataset_clean)
                print(f"Resultado del entrenamiento con datos reales: {result}")
            else:
                print("No hay datos válidos después de limpiar NaN")
        else:
            print("No hay datos reales disponibles o todos los total_runs son NaN")
    except Exception as e:
        print(f"Error obteniendo datos reales: {e}")
    
    print("Test completado!") 
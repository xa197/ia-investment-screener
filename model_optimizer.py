# model_optimizer.py

import streamlit as st
import optuna
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np

# On désactive les logs détaillés d'Optuna pour garder le terminal propre
optuna.logging.set_verbosity(optuna.logging.WARNING)

@st.cache_resource
def optimize_xgboost_hyperparameters(X, y):
    """
    Utilise le framework Optuna pour trouver les meilleurs hyperparamètres
    pour un modèle XGBoost Regressor.
    """
    # On sépare les données en un set d'entraînement et un set de validation
    # Le modèle est entraîné sur le premier et évalué sur le second
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

    def objective(trial):
        """
        La fonction 'objectif' qu'Optuna essaie de minimiser.
        Ici, on veut minimiser l'erreur de prédiction (RMSE).
        """
        # On définit les "plages" de paramètres à tester pour chaque hyperparamètre
        params = {
            'objective': 'reg:squarederror',  # Objectif : prédire une valeur numérique
            'eval_metric': 'rmse',            # Métrique d'évaluation : Root Mean Squared Error
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000, step=100),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'gamma': trial.suggest_float('gamma', 0, 5),
            'random_state': 42,
            'n_jobs': -1  # Utilise tous les cœurs du processeur
        }
        
        model = xgb.XGBRegressor(**params)
        # On utilise "early stopping" pour arrêter l'entraînement si le modèle ne s'améliore plus
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], early_stopping_rounds=50, verbose=False)
        
        preds = model.predict(X_val)
        rmse = np.sqrt(mean_squared_error(y_val, preds))
        return rmse

    # On crée une "étude" Optuna qui va chercher à minimiser le résultat de 'objective'
    study = optuna.create_study(direction='minimize')
    
    # On lance l'optimisation. n_trials est le nombre de combinaisons différentes à tester.
    # Augmenter ce nombre peut donner de meilleurs résultats, mais prend plus de temps.
    study.run(objective, n_trials=25)
    
    print(f"Meilleurs hyperparamètres trouvés par Optuna : {study.best_params}")
    
    # On retourne le dictionnaire des meilleurs paramètres
    return study.best_params
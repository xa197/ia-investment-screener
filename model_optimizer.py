# model_optimizer.py
import streamlit as st
import optuna
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np

# On désactive les logs d'Optuna pour ne pas polluer le terminal
optuna.logging.set_verbosity(optuna.logging.WARNING)

@st.cache_resource
def optimize_xgboost_hyperparameters(X, y):
    """
    Utilise Optuna pour trouver les meilleurs hyperparamètres pour XGBoost.
    """
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

    def objective(trial):
        """La fonction qu'Optuna essaie de minimiser."""
        params = {
            'objective': 'reg:squarederror',
            'eval_metric': 'rmse',
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000, step=100),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'random_state': 42,
            'n_jobs': -1
        }
        
        model = xgb.XGBRegressor(**params)
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], early_stopping_rounds=50, verbose=False)
        preds = model.predict(X_val)
        rmse = np.sqrt(mean_squared_error(y_val, preds))
        return rmse

    study = optuna.create_study(direction='minimize')
    # On limite le nombre d'essais pour que ça ne soit pas trop long
    study.run(objective, n_trials=25, show_progress_bar=True)
    
    print(f"Meilleurs hyperparamètres trouvés : {study.best_params}")
    return study.best_params
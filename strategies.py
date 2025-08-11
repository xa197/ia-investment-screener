# strategies.py (Version Finale avec Diagnostic Amélioré)

import streamlit as st
import pandas as pd
import yfinance as yf
from ta.trend import macd, adx
from ta.momentum import rsi
from ta.volatility import BollingerBands
from ta.volume import on_balance_volume
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb
from backtesting import Strategy
import shap
from model_optimizer import optimize_xgboost_hyperparameters

# Ces imports viennent de tes autres fichiers
from sentiment_analyzer import get_sentiment_analysis
from data_collector import get_hybrid_data_for_backtest

# --- 1. MODÈLES DE CLASSIFICATION (POUR LES ANCIENNES PAGES) ---
@st.cache_resource
def get_trained_model(df, model_type='crypto', model_choice='XGBoost'):
    # ... (code inchangé)
    pass

@st.cache_data(ttl=1800)
def get_ia_signal(ticker, model_choice='XGBoost'):
    # ... (code inchangé)
    pass

# --- NOUVELLE SECTION AMÉLIORÉE : MODÈLE DE RÉGRESSION AVANCÉ ---
@st.cache_resource
def get_trained_optimized_regression_model(df, horizon_days=7):
    """
    Entraîne un modèle de régression OPTIMISÉ et retourne le modèle et l'explainer SHAP.
    Amélioré pour une meilleure gestion des erreurs.
    """
    try:
        df_copy = df.copy()
        
        # Feature Engineering
        df_copy['macd'] = macd(df_copy['Close']); df_copy['rsi'] = rsi(df_copy['Close'])
        bollinger = BollingerBands(close=df_copy['Close'], window=20, window_dev=2); df_copy['bb_width'] = bollinger.bollinger_wband()
        df_copy['day_of_week'] = df_copy.index.dayofweek; df_copy['month'] = df_copy.index.month
        df_copy['pct_change_1'] = df_copy['Close'].pct_change(periods=1)
        df_copy['pct_change_5'] = df_copy['Close'].pct_change(periods=5)
        df_copy['pct_change_21'] = df_copy['Close'].pct_change(periods=21)
        df_copy.dropna(inplace=True)
        
        df_copy['future_price'] = df_copy['Close'].shift(-horizon_days)
        df_copy.dropna(inplace=True)
        
        y = df_copy['future_price']
        features = ['macd', 'rsi', 'bb_width', 'day_of_week', 'month', 'pct_change_1', 'pct_change_5', 'pct_change_21', 'Close', 'Volume']
        X = df_copy[features]
        
        if len(X) < 100:
            print(f"Données insuffisantes après nettoyage : {len(X)} lignes restantes.")
            return None, None, None

        # Optimisation des hyperparamètres
        best_params = optimize_xgboost_hyperparameters(X, y)
        
        # Entraînement final avec les meilleurs paramètres
        model = xgb.XGBRegressor(**best_params, random_state=42)
        model.fit(X, y)
        
        explainer = shap.TreeExplainer(model)
        
        return model, df_copy, features, explainer
    except Exception as e:
        print(f"ERREUR PENDANT L'ENTRAINEMENT OPTIMISÉ: {e}")
        return None, None, None

@st.cache_data(ttl=1800)
def get_ia_optimized_prediction(ticker, horizon_days=7):
    """
    Retourne la prédiction, le potentiel, les données SHAP, et un message de statut.
    """
    try:
        data = yf.Ticker(ticker).history(period="3y")
        if data.empty:
            return None, None, None, "Erreur API: Impossible de télécharger les données de yfinance."

        model, data_with_indicators, features, explainer = get_trained_optimized_regression_model(data, horizon_days)
        
        if model is None:
            return None, None, None, "L'entraînement du modèle a échoué (données insuffisantes après nettoyage)."
        
        last_features = data_with_indicators[features].tail(1)
        predicted_price = model.predict(last_features)[0]
        current_price = last_features['Close'].iloc[0]
        potential_change_pct = ((predicted_price - current_price) / current_price) * 100
        
        shap_values = explainer(last_features)
        
        return float(predicted_price), float(potential_change_pct), (shap_values, last_features), "Analyse réussie."
        
    except Exception as e:
        error_msg = f"Erreur inattendue: {e.__class__.__name__}"
        print(f"Erreur de prédiction optimisée pour {ticker}: {e}")
        return None, None, None, error_msg

# --- CLASSES DE STRATÉGIE POUR LE BACKTESTING ---
# (Ces classes restent inchangées pour l'instant)
# ...
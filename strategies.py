# strategies.py (Version Finale Complète et Stable)

import streamlit as st
import pandas as pd
import yfinance as yf
from ta.trend import macd, adx
from ta.momentum import rsi
from ta.volatility import BollingerBands
from ta.volume import on_balance_volume
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb
from backtesting import Strategy

# Ces imports viennent de tes autres fichiers. Assure-toi qu'ils existent.
from sentiment_analyzer import get_sentiment_analysis
from data_collector import get_hybrid_data_for_backtest
from model_optimizer import optimize_xgboost_hyperparameters


# --- 1. MODÈLES DE CLASSIFICATION (POUR LES SIGNAUX ACHÈTE/VENDS) ---

@st.cache_resource
def get_trained_model(df, model_type='crypto', model_choice='XGBoost'):
    """Entraîne un modèle de CLASSIFICATION sur les données fournies."""
    df_copy = df.copy()
    
    # Indicateurs Techniques
    bollinger = BollingerBands(close=df_copy['Close'], window=20, window_dev=2)
    df_copy['bb_high'] = bollinger.bollinger_hband()
    df_copy['bb_low'] = bollinger.bollinger_lband()
    df_copy['obv'] = on_balance_volume(close=df_copy['Close'], volume=df_copy['Volume'])
    df_copy['macd'] = macd(df_copy['Close'])
    df_copy['rsi'] = rsi(df_copy['Close'])
    df_copy.dropna(inplace=True)
    
    future_days = 5 if model_type == 'crypto' else 10
    df_copy['future_price'] = df_copy['Close'].shift(-future_days)
    df_copy.dropna(inplace=True)
    df_copy['target'] = (df_copy['future_price'] > df_copy['Close']).astype(int)
    
    if model_type == 'crypto':
        features = ['macd', 'rsi', 'bb_high', 'bb_low', 'obv']
    else:
        features = ['macd', 'rsi', 'bb_high', 'bb_low', 'obv', 'sentiment', 'debtToEquity', 'returnOnEquity', 'trailingEps', 'pegRatio']
    
    for col in features:
        if col not in df_copy.columns:
            # st.error(f"Colonne manquante pour l'entraînement : {col}")
            return None, None
            
    X = df_copy[features]
    y = df_copy['target']
    
    if len(X) < 50: return None, None
    
    if model_choice == 'RandomForest':
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    elif model_choice == 'LightGBM':
        model = lgb.LGBMClassifier(random_state=42)
    else:
        model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
        
    model.fit(X, y)
    return model, df_copy


# --- 2. MOTEUR DE PRÉDICTION DE SIGNAUX (CLASSIFICATION) ---

@st.cache_data(ttl=1800)
def get_ia_signal(ticker, model_choice='XGBoost'):
    """Retourne le signal de l'IA (ACHÈTE/NE PAS ACHETER) pour un ticker."""
    try:
        if ticker.endswith("-USD"): # Logique Crypto
            data = yf.Ticker(ticker).history(period="1y")
            if data.empty: return "Données Insuffisantes"
            model, data_with_indicators = get_trained_model(data, model_type='crypto', model_choice=model_choice)
            if model is None: return "Entraînement Échoué"
            last_features = data_with_indicators[['macd', 'rsi', 'bb_high', 'bb_low', 'obv']].tail(1)
            prediction = model.predict(last_features)[0]
            return "ACHÈTE" if prediction == 1 else "NE PAS ACHETER"

        else: # Logique Actions (Hybride)
            data = get_hybrid_data_for_backtest(ticker, period="2y")
            if data is None: return "Données Insuffisantes"
            
            sentiment_score, _, _ = get_sentiment_analysis(ticker)
            data['sentiment'] = sentiment_score
            
            model, data_with_indicators = get_trained_model(data, model_type='action', model_choice=model_choice)
            if model is None: return "Entraînement Échoué"
            
            features = ['macd', 'rsi', 'bb_high', 'bb_low', 'obv', 'sentiment', 'debtToEquity', 'returnOnEquity', 'trailingEps', 'pegRatio']
            last_features = data_with_indicators[features].tail(1)
            prediction = model.predict(last_features)[0]
            return "ACHÈTE" if prediction == 1 else "NE PAS ACHETER"
            
    except Exception as e:
        print(f"ERREUR MOTEUR IA pour {ticker}: {e}")
        return "Erreur Technique"


# --- 3. MODÈLES DE RÉGRESSION (POUR LA PRÉDICTION DE PRIX) ---

@st.cache_resource
def get_trained_regression_model(df, horizon_days=7):
    """Entraîne un modèle de RÉGRESSION avec des features améliorées."""
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
    
    if len(X) < 50: return None, None
    
    model = xgb.XGBRegressor(random_state=42, n_estimators=100, learning_rate=0.1, n_jobs=-1)
    model.fit(X, y)
    
    return model, df_copy, features

@st.cache_data(ttl=1800)
def get_ia_quantitative_prediction(ticker, horizon_days=7):
    """Retourne la prédiction du prix futur en utilisant le modèle de régression amélioré."""
    try:
        data = yf.Ticker(ticker).history(period="2y")
        if data.empty: return None, None
        model, data_with_indicators, features_list = get_trained_regression_model(data, horizon_days)
        if model is None: return None, None
        last_features = data_with_indicators[features_list].tail(1)
        predicted_price = model.predict(last_features)[0]
        current_price = last_features['Close'].iloc[0]
        potential_change_pct = ((predicted_price - current_price) / current_price) * 100
        return float(predicted_price), float(potential_change_pct)
    except Exception as e:
        print(f"Erreur de prédiction quantitative pour {ticker}: {e}")
        return None, None

@st.cache_resource
def get_trained_optimized_regression_model(df, horizon_days=7):
    """Entraîne un modèle de régression OPTIMISÉ et retourne le modèle et l'explainer SHAP."""
    try:
        df_copy = df.copy()
        
        # Feature Engineering (le même que précédemment)
        # ...
        
        if len(X) < 100:
            print(f"Données insuffisantes après nettoyage : {len(X)} lignes restantes.")
            return None, None, None

        best_params = optimize_xgboost_hyperparameters(X, y)
        model = xgb.XGBRegressor(**best_params, random_state=42)
        model.fit(X, y)
        
        explainer = shap.TreeExplainer(model)
        
        return model, df_copy, features, explainer
    except Exception as e:
        print(f"ERREUR PENDANT L'ENTRAINEMENT OPTIMISÉ: {e}")
        return None, None, None

@st.cache_data(ttl=1800)
def get_ia_optimized_prediction(ticker, horizon_days=7):
    """Retourne la prédiction, le potentiel, les données SHAP, et un message de statut."""
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


# --- 4. CLASSES DE STRATÉGIE POUR LE BACKTESTING ---
def indicator_wrapper(indicator_func, data, **kwargs):
    return indicator_func(pd.Series(data), **kwargs).values

class MLStrategyOpt(Strategy):
    # ... (code complet de la stratégie)

class HybridStrategy(Strategy):
    # ... (code complet de la stratégie)
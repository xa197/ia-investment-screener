# predictor.py
import pandas as pd
from ta.trend import macd, adx
from ta.momentum import rsi
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def get_historical_data(ticker_symbol, period="1y"):
    """Récupère les données historiques et calcule les indicateurs techniques."""
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period=period)
    
    if df.empty:
        return None
        
    # Calcul des indicateurs techniques
    df['macd'] = macd(df['Close'])
    df['adx'] = adx(df['High'], df['Low'], df['Close'])
    df['rsi'] = rsi(df['Close'])
    
    # On supprime les lignes avec des données manquantes (générées par les indicateurs)
    df.dropna(inplace=True)
    
    # --- Création de la cible (ce qu'on veut prédire) ---
    # Si le prix de clôture dans 5 jours est plus haut qu'aujourd'hui, la cible est 1 (Achète)
    # Sinon, la cible est 0 (Vends/Garde)
    future_days = 5
    df['future_price'] = df['Close'].shift(-future_days)
    df.dropna(inplace=True)
    df['target'] = (df['future_price'] > df['Close']).astype(int)
    
    return df

def train_model_and_predict(ticker_symbol):
    """Entraîne un modèle pour un ticker et prédit le signal actuel."""
    df = get_historical_data(ticker_symbol)
    
    if df is None or len(df) < 50: # Pas assez de données pour entraîner
        return "Données Insuffisantes"
        
    # Définir les features (nos indicateurs) et la cible
    features = ['macd', 'adx', 'rsi']
    X = df[features]
    y = df['target']
    
    # Diviser les données : 80% pour entraîner, 20% pour tester
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
    
    if len(X_train) == 0:
        return "Données Insuffisantes"

    # Créer et entraîner le modèle (Random Forest)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Évaluer la précision sur les données de test (pour info)
    accuracy = model.score(X_test, y_test)
    print(f"Précision du modèle pour {ticker_symbol}: {accuracy:.2f}")
    
    # Faire une prédiction sur la dernière donnée disponible
    last_data = X.tail(1)
    prediction = model.predict(last_data)
    
    # Traduire la prédiction en signal
    if prediction[0] == 1:
        return "ACHÈTE"
    else:
        # Pour distinguer "Vends" et "Garde", on regarde le momentum (RSI)
        # C'est une heuristique simple
        last_rsi = last_data['rsi'].iloc[0]
        if last_rsi > 70: # Le marché est suracheté, risque de baisse
            return "VENDS"
        else:
            return "GARDE"
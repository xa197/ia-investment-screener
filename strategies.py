import pandas as pd
import numpy as np
from datetime import date, timedelta
from backtesting import Strategy
from backtesting.lib import crossover
from sklearn.linear_model import LinearRegression
import streamlit as st 

# On importe la fonction pour récupérer les données
from utils import get_stock_data


# --- Stratégies de Backtesting ---
class SmaCross(Strategy):
    n1 = 10; n2 = 30
    def init(self):
        close = pd.Series(self.data.Close)
        self.sma1 = self.I(lambda: close.rolling(self.n1).mean())
        self.sma2 = self.I(lambda: close.rolling(self.n2).mean())
    def next(self):
        if crossover(self.sma1, self.sma2): self.buy()
        elif crossover(self.sma2, self.sma1): self.sell()


# --- Fonctions de Prédiction Quantitative ---

def get_ia_quantitative_prediction(ticker, horizon_days=90):
    """
    Calcule le potentiel de croissance d'un ticker en utilisant une régression linéaire.
    """
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=2*365)
        data = get_stock_data(ticker, start_date, end_date)

        if data is None or data.empty or len(data) < 50:
            return None, None 

        df_pred = data[['Date', 'Close']].copy()
        df_pred.dropna(inplace=True)
        df_pred['Days'] = (df_pred['Date'] - df_pred['Date'].min()).dt.days
        
        X = df_pred[['Days']]
        y = df_pred['Close']

        model = LinearRegression()
        model.fit(X, y)

        last_day = X['Days'].max()
        future_day = np.array([[last_day + horizon_days]])
        predicted_price = model.predict(future_day)[0]

        current_price = y.iloc[-1]
        if current_price > 0:
            potential_change = ((predicted_price - current_price) / current_price) * 100
        else:
            return None, None

        return predicted_price, potential_change

    except Exception as e:
        return None, None

# --- CORRECTION APPLIQUÉE ICI ---
class HybridStrategy(Strategy):
    """
    Future stratégie combinant plusieurs indicateurs ou modèles.
    L'instruction 'pass' est nécessaire pour que le fichier soit syntaxiquement correct.
    """
    pass
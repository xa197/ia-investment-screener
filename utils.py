import streamlit as st
import yfinance as yf
from plotly import graph_objs as go
from datetime import date
from retry import retry
import requests_cache

# Configuration d'une session de requêtes robuste
# Elle garde en cache les réponses pour ne pas redemander inutilement
# et s'identifie avec un User-Agent pour paraître moins comme un script automatisé
session = requests_cache.CachedSession('yfinance.cache')
session.headers['User-agent'] = 'my-program/1.0'

# Le décorateur @st.cache_data est CRUCIAL pour que Streamlit ne relance pas la fonction sans arrêt
@st.cache_data
# Le décorateur @retry va automatiquement réessayer la fonction si elle échoue
@retry(tries=3, delay=1, backoff=2) # Tente 3 fois, attend 1s, puis 2s...
def get_stock_data(ticker, start_date, end_date):
    """
    Récupère les données historiques pour un ticker donné depuis Yahoo Finance.
    Utilise une session avec cache et des tentatives multiples pour plus de robustesse.
    """
    try:
        # On utilise la session robuste que l'on a configurée plus haut
        data = yf.download(
            tickers=ticker, 
            start=start_date, 
            end=end_date, 
            session=session,
            progress=False # On désactive la barre de progression de yfinance
        )
        if data.empty:
            return None
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        # Si après 3 tentatives ça ne marche toujours pas, on abandonne pour ce ticker
        return None

def plot_raw_data(data):
    """
    Affiche un graphique simple du cours de clôture.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="Cours d'ouverture"))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="Cours de clôture"))
    fig.update_layout(
        title_text='Évolution du cours',
        xaxis_rangeslider_visible=True,
        xaxis_title="Date",
        yaxis_title="Prix (USD)"
    )
    return fig
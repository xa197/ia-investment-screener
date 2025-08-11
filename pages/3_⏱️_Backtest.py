# pages/3_⏱️_Backtest.py (version finale corrigée)
import streamlit as st
import yfinance as yf
from backtesting import Backtest
from strategies import MLStrategyOpt, HybridStrategy
from data_collector import get_hybrid_data_for_backtest
from sentiment_analyzer import get_sentiment_analysis # On importe l'analyseur

@st.cache_data
def get_historical_data_for_crypto(ticker_symbol, period="1y"):
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period=period)
    if df.empty: return None
    return df

st.set_page_config(page_title="Backtesting Avancé", layout="wide")
st.title("🚀 Backtesting de Stratégies Avancées")
st.info("Cette page vous permet de backtester différentes stratégies d'IA.")

strategy_choice = st.selectbox(
    "Choisissez le type d'analyse :",
    ("Crypto (Technique Pure)", "Actions (Hybride : Technique + Fondamental + Sentiment)")
)
if strategy_choice == "Crypto (Technique Pure)":
    ticker_input = st.text_input("Entrez un ticker de Crypto (ex: BTC-USD)", "ETH-USD")
    strategy_to_run = MLStrategyOpt
    data_function = get_historical_data_for_crypto
else:
    ticker_input = st.text_input("Entrez un ticker d'Action (ex: AAPL, NVDA)", "NVDA")
    strategy_to_run = HybridStrategy
    data_function = get_hybrid_data_for_backtest

period_input = st.selectbox("Période de données", ["2y", "5y"], index=0)

if st.button("🚀 Lancer le Backtest"):
    if not ticker_input: st.error("Veuillez entrer un ticker.")
    else:
        ticker = ticker_input.strip().upper()
        with st.spinner(f"Backtesting de la stratégie pour {ticker}..."):
            try:
                data = data_function(ticker, period=period_input)
                if data is None or len(data) < 100:
                    st.error("Pas assez de données pour le backtest.")
                else:
                    # --- LA CORRECTION EST ICI ---
                    if strategy_to_run == HybridStrategy:
                        # 1. On calcule le score de sentiment
                        st.write("Analyse du sentiment des actualités...")
                        sentiment_score, _, _ = get_sentiment_analysis(ticker)
                        # 2. On ajoute la colonne 'sentiment' à TOUT notre tableau de données
                        data['sentiment'] = sentiment_score
                    
                    strategy_to_run.model = None
                    bt = Backtest(data, strategy_to_run, cash=10000, commission=.002)
                    stats = bt.run()
                    
                    st.subheader("Résultats du Backtest")
                    st.write(stats)
                    st.subheader("Graphique de Performance")
                    fig = bt.plot()
                    st.pyplot(fig)
            except Exception as e:
                st.error(f"Une erreur est survenue : {e}"); st.exception(e)
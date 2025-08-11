# pages/7_🔮_Prédictions_Quantitatives.py

import streamlit as st
import pandas as pd
import yfinance as yf # <-- LA LIGNE DE CORRECTION
# On importe la nouvelle fonction de prédiction
from strategies import get_ia_quantitative_prediction

st.set_page_config(page_title="Prédictions Quantitatives", layout="wide")
st.title("🔮 Prédictions Quantitatives de l'IA")
st.warning("⚠️ Ces prédictions sont le résultat de modèles statistiques et sont hautement spéculatives. Elles ne représentent en aucun cas une garantie de performance future.")

# --- INTERFACE DE CONTRÔLE ---
st.header("1. Paramètres de la Prédiction")

col1, col2 = st.columns(2)
with col1:
    ticker_input = st.text_input("Entrez un ticker à analyser (Action ou Crypto)", "NVDA")
with col2:
    # On peut maintenant choisir l'horizon de prédiction
    horizon_map = {"1 Semaine": 7, "1 Mois": 30, "3 Mois": 90}
    horizon_choice = st.selectbox("Horizon de prédiction :", horizon_map.keys())
    horizon_days = horizon_map[horizon_choice]

if st.button(f"🔮 Lancer la prédiction pour {ticker_input} à {horizon_choice}"):
    ticker = ticker_input.strip().upper()
    with st.spinner(f"Entraînement du modèle de régression pour {ticker}..."):
        
        predicted_price, potential_change = get_ia_quantitative_prediction(ticker, horizon_days)
        
        st.header("2. Résultats de la Prédiction")
        if predicted_price is None:
            st.error("L'analyse n'a pas pu être complétée. Les données sont peut-être insuffisantes.")
        else:
            current_price = yf.Ticker(ticker).history(period="1d")['Close'].iloc[0]
            
            st.metric(
                label=f"Prédiction du prix dans {horizon_choice}",
                value=f"${predicted_price:,.2f}",
                delta=f"{potential_change:,.2f} % vs actuel"
            )
            
            st.write(f"Prix actuel : ${current_price:,.2f}")
            st.caption(f"Le modèle de régression (XGBoost) a été entraîné sur 2 ans de données pour prédire le prix de clôture dans {horizon_days} jours.")
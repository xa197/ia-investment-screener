# app.py
import streamlit as st
import pandas as pd
from data_collector import get_stock_data
from scorer import calculate_scores

st.set_page_config(page_title="IA Investment Screener", layout="wide")
st.title("🤖 IA Investment Screener")
st.write("Ce logiciel analyse des actions pour trouver des opportunités. **Ceci n'est pas un conseil financier.**")

st.sidebar.header("Paramètres d'Analyse")
default_tickers = "AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, JNJ, V, WMT"
tickers_input = st.sidebar.text_area("Tickers (séparés par virgules) :", default_tickers, height=150)
TICKERS = [ticker.strip().upper() for ticker in tickers_input.split(',') if ticker.strip()]

if st.sidebar.button("🚀 Lancer l'analyse"):
    if not TICKERS:
        st.error("Veuillez entrer au moins un ticker.")
    else:
        with st.spinner("Analyse en cours..."):
            raw_data = get_stock_data(TICKERS)
        
        # On vérifie juste si on a reçu des données, peu importe si elles sont complètes
        if raw_data.empty:
            st.error("Aucune donnée n'a pu être récupérée. Vérifiez les tickers.")
        else:
            # On envoie directement les données brutes au scorer, qui va se débrouiller avec !
            scored_stocks = calculate_scores(raw_data)
            
            final_df = scored_stocks.sort_values(by='Score Final', ascending=False)
            
            st.header("🏆 Classement des Actions")
            # On affiche les colonnes clés pour la décision
            display_cols = ['Ticker', 'Nom', 'Secteur', 'Score Final', 'Ratio P/E', 'Marge Bénéficiaire', 'Croissance Revenus Trim.']
            st.dataframe(final_df[display_cols])
            
            st.header("📊 Visualisation du Score Final")
            st.bar_chart(final_df.set_index('Nom')['Score Final'])
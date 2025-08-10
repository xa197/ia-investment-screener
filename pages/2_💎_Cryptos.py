# pages/2_💎_Cryptos.py
import streamlit as st
import yfinance as yf # On doit l'importer car predictor.py l'utilise
from predictor import train_model_and_predict

st.set_page_config(page_title="IA Crypto Predictor", layout="wide")
st.title("🤖 IA Crypto Predictor")
st.warning("⚠️ Les signaux sont générés par une IA expérimentale et ne constituent pas un conseil financier. Utilisez à vos propres risques.")

# Input pour un seul ticker à la fois, car l'analyse est plus lourde
ticker_input = st.text_input("Entrez un ticker de crypto (ex: BTC-USD)", "BTC-USD")

if st.button("🧠 Lancer l'analyse prédictive"):
    if not ticker_input:
        st.error("Veuillez entrer un ticker.")
    else:
        ticker = ticker_input.strip().upper()
        with st.spinner(f"Analyse en profondeur de {ticker}... Entraînement du modèle..."):
            try:
                # On lance la fonction qui fait tout : collecte, entraînement et prédiction
                signal = train_model_and_predict(ticker)

                st.subheader(f"Signal Actuel pour {ticker}")
                
                if signal == "ACHÈTE":
                    st.success(f"Signal : **{signal}**")
                    st.write("Le modèle prédit une probabilité de hausse du prix dans les 5 prochains jours.")
                elif signal == "VENDS":
                    st.error(f"Signal : **{signal}**")
                    st.write("Le modèle prédit une probabilité de baisse ou de stagnation, et les indicateurs de momentum sont élevés (risque de retournement).")
                elif signal == "GARDE":
                    st.info(f"Signal : **{signal}**")
                    st.write("Le modèle ne prédit pas une hausse significative. La tendance actuelle est neutre ou baissière mais sans signe de surachat.")
                else: # Cas d'erreur comme "Données Insuffisantes"
                    st.warning(signal)
            
            except Exception as e:
                st.error(f"Une erreur est survenue pendant l'analyse : {e}")
# pages/9_🔬_Analyse_Approfondie.py (Version avec Messages d'Erreur Détaillés)

import streamlit as st
import shap
import streamlit.components.v1 as components
from strategies import get_ia_optimized_prediction
import yfinance as yf
import matplotlib.pyplot as plt

# Fonction pour afficher les graphiques SHAP
def st_shap(plot, height=None):
    shap_html = f"<head>{shap.getjs()}</head><body>{plot.html()}</body>"
    components.html(shap_html, height=height)

st.set_page_config(page_title="Analyse Approfondie", layout="wide")
st.title("🔬 Analyse Approfondie par l'IA")
st.info("Cette page utilise un modèle optimisé pour chaque analyse et explique en détail ses prédictions à l'aide de SHAP.")

# --- Interface de Contrôle ---
st.header("1. Paramètres de l'Analyse")
col1, col2 = st.columns(2)
with col1:
    ticker_input = st.text_input("Entrez un ticker à analyser (Action ou Crypto)", "NVDA")
with col2:
    horizon_map = {"1 Semaine": 7, "1 Mois": 30}
    horizon_choice = st.selectbox("Horizon de prédiction :", horizon_map.keys())
    horizon_days = horizon_map[horizon_choice]

if st.button(f"🚀 Lancer l'Analyse Approfondie pour {ticker_input}"):
    ticker = ticker_input.strip().upper()
    
    with st.spinner(f"Optimisation des hyperparamètres pour {ticker}... (cela peut prendre plusieurs minutes)"):
        # La fonction retourne maintenant 4 valeurs, dont le message de statut
        predicted_price, potential_change, shap_data, status_message = get_ia_optimized_prediction(ticker, horizon_days)
        
    st.header("2. Résultat de la Prédiction Optimisée")
    if predicted_price is None:
        # On affiche le message d'erreur précis retourné par la fonction
        st.error(f"L'analyse n'a pas pu être complétée. Raison : {status_message}")
    else:
        current_price = yf.Ticker(ticker).history(period="1d")['Close'].iloc[0]
        st.metric(
            label=f"Prédiction du prix dans {horizon_choice}",
            value=f"${predicted_price:,.2f}",
            delta=f"{potential_change:,.2f} % vs actuel (${current_price:,.2f})"
        )
        
        st.header("3. Explication de la Décision de l'IA")
        if shap_data:
            shap_values, last_features = shap_data
            st.subheader("Forces Poussant la Prédiction")
            st.write("En rouge, les facteurs haussiers. En bleu, les facteurs baissiers.")
            st_shap(shap.force_plot(shap_values.base_values[0], shap_values.values[0], last_features))
            
            st.subheader("Cascade des Contributions")
            fig, ax = plt.subplots(figsize=(10, 4), dpi=150)
            shap.plots.waterfall(shap_values[0], show=False)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("Les données d'explicabilité n'ont pas pu être générées.")
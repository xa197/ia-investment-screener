# pages/9_🔬_Analyse_Approfondie.py (Version Finale Complète et Stable)

import streamlit as st
import shap
import streamlit.components.v1 as components
import yfinance as yf
import matplotlib.pyplot as plt

# On importe la fonction la plus avancée depuis notre moteur d'IA
from strategies import get_ia_optimized_prediction

# Fonction utilitaire pour afficher les graphiques SHAP dans Streamlit
def st_shap(plot, height=None):
    """Affiche un graphique SHAP dans Streamlit en l'encapsulant dans du HTML."""
    shap_html = f"<head>{shap.getjs()}</head><body>{plot.html()}</body>"
    components.html(shap_html, height=height)

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Analyse Approfondie", layout="wide")
st.title("🔬 Analyse Approfondie par l'IA")
st.info("Cette page utilise un modèle optimisé pour chaque analyse et explique en détail ses prédictions à l'aide de la technologie SHAP (SHapley Additive exPlanations).")
st.warning("L'optimisation des hyperparamètres peut prendre plusieurs minutes.")


# --- INTERFACE DE CONTRÔLE ---
st.header("1. Paramètres de l'Analyse")
col1, col2 = st.columns(2)
with col1:
    ticker_input = st.text_input("Entrez un ticker à analyser (Action ou Crypto)", "NVDA")
with col2:
    horizon_map = {"1 Semaine": 7, "1 Mois": 30}
    horizon_choice = st.selectbox("Horizon de prédiction :", horizon_map.keys())
    horizon_days = horizon_map[horizon_choice]

# --- BOUTON DE LANCEMENT ET LOGIQUE D'ANALYSE ---
if st.button(f"🚀 Lancer l'Analyse Approfondie pour {ticker_input}"):
    ticker = ticker_input.strip().upper()
    
    # On affiche un message pendant le long processus d'optimisation
    with st.spinner(f"Optimisation des hyperparamètres et entraînement du modèle pour {ticker}..."):
        # La fonction retourne 4 valeurs, dont le message de statut
        predicted_price, potential_change, shap_data, status_message = get_ia_optimized_prediction(ticker, horizon_days)
        
    st.header("2. Résultat de la Prédiction Optimisée")
    if predicted_price is None:
        # Si la prédiction a échoué, on affiche le message d'erreur précis
        st.error(f"L'analyse n'a pas pu être complétée. Raison : {status_message}")
    else:
        # Si la prédiction a réussi, on affiche les résultats
        try:
            current_price = yf.Ticker(ticker).history(period="1d")['Close'].iloc[0]
            st.metric(
                label=f"Prédiction du prix dans {horizon_choice}",
                value=f"${predicted_price:,.2f}",
                delta=f"{potential_change:,.2f} % vs actuel (${current_price:,.2f})"
            )
        except IndexError:
            st.metric(
                label=f"Prédiction du prix dans {horizon_choice}",
                value=f"${predicted_price:,.2f}",
                delta=f"{potential_change:,.2f} %"
            )

        # --- SECTION D'EXPLICABILITÉ (XAI) AVEC SHAP ---
        st.header("3. Explication de la Décision de l'IA")
        
        if shap_data:
            shap_values, last_features = shap_data
            
            st.subheader("Forces Poussant la Prédiction")
            st.write("Ce graphique montre les facteurs qui ont influencé la prédiction. En rouge, les facteurs haussiers (qui ont augmenté le prix prédit). En bleu, les facteurs baissiers.")
            # Le force_plot explique une seule prédiction
            st_shap(shap.force_plot(shap_values.base_values[0], shap_values.values[0], last_features))
            
            st.subheader("Cascade des Contributions")
            st.write("Une autre vue montrant comment chaque indicateur a contribué à passer du prix de base moyen à la prédiction finale.")
            # Pour afficher le graphique matplotlib, il faut le créer explicitement
            # On utilise un bloc try-except au cas où la figure ne pourrait être générée
            try:
                fig, ax = plt.subplots(figsize=(10, 4), dpi=150)
                shap.plots.waterfall(shap_values[0], show=False)
                plt.tight_layout()
                st.pyplot(fig)
            except Exception as e:
                st.warning(f"Impossible de générer le graphique en cascade. Erreur: {e}")
        else:
            st.warning("Les données d'explicabilité n'ont pas pu être générées.")
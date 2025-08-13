# Importations des bibliothèques nécessaires
import streamlit as st
from datetime import date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import pandas as pd

# Importations depuis votre module d'utilitaires
from utils import get_stock_data, plot_raw_data

# Configuration de la page Streamlit
st.set_page_config(layout="wide", page_title="Crypto Predictor", page_icon="💎")

# --- INTERFACE UTILISATEUR (SIDEBAR) ---
st.sidebar.header("Paramètres de Sélection")

# Liste de quelques crypto-monnaies populaires pour l'exemple
# L'utilisateur peut entrer n'importe quel ticker valide sur Yahoo Finance
cryptos = ("BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD")
selected_crypto = st.sidebar.text_input("Sélectionnez une crypto-monnaie (ex: BTC-USD)", "BTC-USD")

# Sélection des dates
start_date = st.sidebar.date_input("Date de début", date(2019, 1, 1))
end_date = st.sidebar.date_input("Date de fin", date.today())

# Bouton pour lancer l'analyse (même si Streamlit se met à jour automatiquement)
st.sidebar.button('Analyser')


# --- CORPS PRINCIPAL DE L'APPLICATION ---
st.title("💎 Crypto Predictor")
st.write("Cet outil vous permet d'analyser et de prédire le cours des crypto-monnaies.")
st.write("---")

# Chargement et affichage des données
if selected_crypto:
    with st.spinner(f'Chargement des données pour {selected_crypto}...'):
        data = get_stock_data(selected_crypto, start_date, end_date)

    if not data.empty:
        st.subheader(f'Données brutes pour {selected_crypto}')
        st.write("Aperçu des 5 dernières observations :")
        st.write(data.tail())

        # Affichage du graphique des données brutes
        st.subheader(f'Évolution du cours de clôture de {selected_crypto}')
        fig = plot_raw_data(data)
        st.plotly_chart(fig, use_container_width=True)

        # --- SECTION DE PRÉDICTION AVEC PROPHET ---
        st.subheader('Prédiction du cours à long terme avec Prophet')
        
        # Slider pour choisir le nombre d'années de prédiction
        n_years = st.slider('Années de prédiction:', 1, 5, 1)
        period = n_years * 365

        # Préparation des données pour Prophet
        # Prophet requiert des colonnes nommées 'ds' (date) et 'y' (valeur à prédire)
        df_train = data[['Date', 'Close']].rename(columns={"Date": "ds", "Close": "y"})
        
        with st.spinner('Entraînement du modèle de prédiction...'):
            # Création et entraînement du modèle
            m = Prophet(
                daily_seasonality=True,
                weekly_seasonality=True,
                yearly_seasonality=True,
                seasonality_mode='multiplicative' # Plus adapté aux séries financières
            )
            m.fit(df_train)

        with st.spinner('Génération des prédictions...'):
            # Création du dataframe futur pour la prédiction
            future = m.make_future_dataframe(periods=period)
            forecast = m.predict(future)

        # Affichage des résultats de la prédiction
        st.subheader('Données de prévision')
        st.write("Aperçu des dernières données prédites :")
        st.write(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

        # Graphique de la prédiction
        st.subheader(f'Graphique de prévision pour {n_years} année(s)')
        fig1 = plot_plotly(m, forecast)
        fig1.update_layout(
            title=f'Prévision du cours pour {selected_crypto}',
            xaxis_title='Date',
            yaxis_title='Cours de clôture (USD)'
        )
        st.plotly_chart(fig1, use_container_width=True)

        # Graphique des composantes de la prédiction
        st.subheader("Composantes de la prévision")
        fig2 = m.plot_components(forecast)
        st.write(fig2)

    else:
        st.error(f"Aucune donnée trouvée pour '{selected_crypto}'. Veuillez vérifier le ticker ou la plage de dates.")

else:
    st.info("Veuillez sélectionner une crypto-monnaie dans la barre latérale pour commencer l'analyse.")
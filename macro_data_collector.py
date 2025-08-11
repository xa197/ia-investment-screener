# macro_data_collector.py
import streamlit as st
import pandas as pd
import pandas_datareader.data as web
from datetime import datetime

# Liste des indicateurs FRED que nous voulons suivre
FRED_INDICATORS = {
    'FED_FUNDS_RATE': 'DFF',       # Taux d'intérêt
    'INFLATION_CPI': 'CPIAUCSL',   # Inflation (mensuel)
    'UNEMPLOYMENT_RATE': 'UNRATE', # Taux de chômage (mensuel)
    'VIX': 'VIXCLS'                # Indice de volatilité VIX (journalier)
}

@st.cache_data(ttl=86400) # On met en cache les données pour 24h
def get_macro_data(start_date, end_date):
    """
    Récupère les données macroéconomiques de la FRED pour une période donnée.
    """
    try:
        # On télécharge toutes les séries de données en une seule fois
        df_macro = web.DataReader(list(FRED_INDICATORS.values()), 'fred', start_date, end_date)
        df_macro.columns = list(FRED_INDICATORS.keys()) # On renomme les colonnes pour la lisibilité
        
        # --- Nettoyage des données ---
        # Les données mensuelles (inflation, chômage) ont des valeurs manquantes les autres jours.
        # On propage la dernière valeur connue aux jours suivants (forward fill).
        df_macro[['INFLATION_CPI', 'UNEMPLOYMENT_RATE']] = df_macro[['INFLATION_CPI', 'UNEMPLOYMENT_RATE']].fillna(method='ffill')
        
        # Il peut rester des valeurs manquantes au tout début, on les remplace par 0.
        df_macro.fillna(0, inplace=True)
        
        return df_macro
    except Exception as e:
        print(f"Erreur lors de la récupération des données macro : {e}")
        return pd.DataFrame() # Retourne un DataFrame vide en cas d'erreur
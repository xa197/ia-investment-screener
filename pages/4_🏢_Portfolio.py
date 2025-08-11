# pages/4_🏢_Portfolio.py (Version Finale Corrigée)
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from strategies import get_ia_signal

st.set_page_config(page_title="Mon Portfolio Virtuel", layout="wide")
st.title("🏢 Mon Portfolio Virtuel")

PORTFOLIO_FILE = 'portfolio.csv'

# --- Fonctions ---
# ... (les fonctions add_manual_trade, get_current_price, get_price_on_date restent les mêmes) ...

@st.cache_data(ttl=300)
def get_current_price(ticker):
    try: return yf.Ticker(ticker).history(period="1d")['Close'].iloc[-1]
    except: return 0

def update_positions_with_current_values(df):
    """Met à jour un DataFrame de positions avec les prix actuels."""
    if df.empty: return df
    tickers = df['Ticker'].unique()
    current_prices = {ticker: get_current_price(ticker) for ticker in tickers}
    df['Prix Actuel'] = df['Ticker'].map(current_prices)
    df['Valeur Actuelle'] = df['Quantite'] * df['Prix Actuel']
    df['Gain/Perte'] = df['Valeur Actuelle'] - df['Valeur']
    df['Gain/Perte (%)'] = (df['Gain/Perte'] / df['Valeur']) * 100
    return df

def load_data():
    try:
        return pd.read_csv(PORTFOLIO_FILE)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['Date','Ticker','Action','Quantite','Prix','Valeur','Type'])

# --- AFFICHAGE PRINCIPAL ---
portfolio_df = load_data()

st.header("Vue d'Ensemble du Portfolio")
portfolio_view = st.selectbox("Afficher le portfolio :", ('Tous', 'Réel', 'Fictif'))

# Filtre le DataFrame en fonction du choix
filtered_df = portfolio_df
if portfolio_view != 'Tous':
    filtered_df = portfolio_df[portfolio_df['Type'] == portfolio_view]

if not filtered_df.empty:
    positions = filtered_df.groupby('Ticker').agg(Quantite=('Quantite', 'sum'), Valeur=('Valeur', 'sum')).reset_index()
    positions = positions[positions['Quantite'] > 1e-6]
    
    if not positions.empty:
        # --- LA LIGNE DE CORRECTION EST ICI ---
        positions = update_positions_with_current_values(positions)
        
        tickers = positions['Ticker'].unique()
        with st.spinner("Récupération des signaux IA..."):
            signals = {ticker: get_ia_signal(ticker) for ticker in tickers}
        positions['Signal IA'] = positions['Ticker'].map(signals)
        
        # Calcul des totaux après mise à jour
        total_invested = positions['Valeur'].sum()
        total_current_value = positions['Valeur Actuelle'].sum()
        total_gain_loss = total_current_value - total_invested
        total_gain_loss_percent = (total_gain_loss / total_invested) * 100 if total_invested > 0 else 0
        
        col1, col2 = st.columns(2)
        col1.metric("Valeur Actuelle", f"${total_current_value:,.2f}", f"${total_gain_loss:,.2f} ({total_gain_loss_percent:.2f}%)")
        col2.metric("Total Investi", f"${total_invested:,.2f}")
        
        st.header("Mes Positions")
        # On définit l'ordre des colonnes pour être sûr
        display_columns = ['Ticker', 'Signal IA', 'Quantite', 'Valeur', 'Prix Actuel', 'Valeur Actuelle', 'Gain/Perte', 'Gain/Perte (%)']
        st.dataframe(positions[display_columns].style.format({
            'Valeur': '${:,.2f}', 'Prix Actuel': '${:,.2f}', 'Valeur Actuelle': '${:,.2f}',
            'Gain/Perte': '${:,.2f}', 'Gain/Perte (%)': '{:.2f}%', 'Quantite': '{:.6f}'
        }))
else:
    st.info(f"Le portfolio '{portfolio_view}' est vide.")

# ... (Le reste du code pour l'ajout manuel et la gestion reste le même) ...
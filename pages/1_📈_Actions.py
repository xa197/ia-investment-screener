# pages/1_📈_Actions.py (Version Finale Complète et Stable)

import streamlit as st
import pandas as pd
from datetime import datetime
import yfinance as yf

# On importe les fonctions nécessaires depuis nos autres modules
# Note : on a besoin d'un "scorer" simple qui n'est plus dans strategies.py. On le recrée ici.
from data_collector import get_stock_data_for_actions
from sklearn.preprocessing import MinMaxScaler

# --- Logique du Scorer (intégrée ici pour la simplicité) ---
@st.cache_data
def calculate_scores(df):
    """Attribue un score à chaque action basé sur des métriques normalisées."""
    df_scored = df.copy()
    metrics_weights = {
        'Ratio P/E': -0.2, 'Ratio Cours/Ventes': -0.1, 'Marge Bénéficiaire': 0.4
    }
    df_scored['Score Final'] = 0.0
    scaler = MinMaxScaler()
    for metric, weight in metrics_weights.items():
        if metric in df_scored.columns and pd.api.types.is_numeric_dtype(df_scored[metric]):
            # On remplit les valeurs manquantes avec la médiane avant de normaliser
            median_val = df_scored[metric].median()
            df_scored[metric].fillna(median_val, inplace=True)
            
            scaled_values = scaler.fit_transform(df_scored[[metric]])
            if weight < 0:
                score_component = (1 - scaled_values) * abs(weight)
            else:
                score_component = scaled_values * weight
            df_scored['Score Final'] += score_component.flatten()
    return df_scored

# --- Fonctions d'Ajout au Portfolio ---
@st.cache_data(ttl=3600)
def get_exchange_rate(currency):
    if currency == 'USD': return 1.0
    try: return yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[0]
    except Exception as e: st.warning(f"Taux de change indisponible. Erreur: {e}"); return 1.0

def add_to_portfolio(ticker, montant_investi, devise, portfolio_type):
    try:
        prix_actuel_usd = yf.Ticker(ticker).history(period="1d")['Close'].iloc[0]
        if prix_actuel_usd == 0:
            st.error(f"Prix indisponible pour {ticker}. Achat annulé."); return
            
        montant_investi_usd = montant_investi * get_exchange_rate(devise) if devise == 'EUR' else montant_investi
        quantite = montant_investi_usd / prix_actuel_usd
        
        new_trade = pd.DataFrame([{
            'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Ticker': ticker,
            'Action': 'ACHAT', 'Quantite': quantite, 'Prix': prix_actuel_usd,
            'Valeur': montant_investi_usd, 'Type': portfolio_type
        }])
        
        try:
            portfolio_df = pd.read_csv('portfolio.csv')
            portfolio_df = pd.concat([portfolio_df, new_trade], ignore_index=True)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            portfolio_df = new_trade
            
        portfolio_df.to_csv('portfolio.csv', index=False)
        st.success(f"Achat de {quantite:.4f} parts de {ticker} ajouté au portfolio '{portfolio_type}'!")
    except Exception as e:
        st.error(f"Erreur lors de l'ajout au portfolio : {e}")

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="IA Stock Screener", layout="wide")
st.title("🏆 IA Stock Screener (Scoring)")
st.info("Cette page analyse une liste d'actions sur la base de critères fondamentaux et leur attribue un score. Un score plus élevé est meilleur.")

# Sidebar pour les paramètres
st.sidebar.header("Paramètres d'Analyse")
default_tickers = "AAPL, MSFT, GOOGL, AMZN, NVDA, META, JNJ, V, WMT, JPM"
tickers_input = st.sidebar.text_area("Tickers (séparés par virgules) :", default_tickers, height=150)
TICKERS = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]

if st.sidebar.button("🚀 Lancer le scoring"):
    if not TICKERS:
        st.error("Veuillez entrer au moins un ticker.")
    else:
        with st.spinner("Analyse du scoring en cours..."):
            raw_data = get_stock_data_for_actions(TICKERS)
        
        if not raw_data.empty:
            scored_stocks = calculate_scores(raw_data)
            final_df = scored_stocks.sort_values(by='Score Final', ascending=False)
            st.session_state['scored_stocks'] = final_df # On stocke le résultat pour qu'il persiste
        else:
            st.warning("Aucune donnée n'a pu être récupérée pour ces tickers.")

# Affichage des résultats
if 'scored_stocks' in st.session_state:
    st.header("Classement des Actions")
    df_results = st.session_state['scored_stocks']
    st.dataframe(df_results)

    st.header("➕ Ajouter une Action au Portfolio (Achat d'Aujourd'hui)")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        ticker_to_add = st.selectbox("Ticker :", df_results['Ticker'].tolist())
    with col2:
        amount_to_invest = st.number_input("Montant :", min_value=1.0, value=100.0, step=10.0, format="%.2f")
    with col3:
        currency = st.selectbox("Devise :", ('USD', 'EUR'))
    with col4:
        p_type = st.selectbox("Type de Portfolio :", ('Fictif', 'Réel'))
        
    if st.button(f"Investir {amount_to_invest:,.2f} {currency} dans {ticker_to_add}"):
        add_to_portfolio(ticker_to_add, amount_to_invest, currency, p_type)
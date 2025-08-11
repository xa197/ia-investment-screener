# pages/1_📈_Actions.py (Version avec Type de Portfolio)
import streamlit as st; import pandas as pd; from datetime import datetime; import yfinance as yf
from data_collector import get_stock_data_for_actions; from scorer import calculate_scores
@st.cache_data(ttl=3600)
def get_exchange_rate(currency):
    if currency == 'USD': return 1.0
    try: return yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[0]
    except Exception as e: st.warning(f"Taux de change indisponible. Erreur: {e}"); return 1.0

def add_to_portfolio(ticker, montant_investi, devise, portfolio_type): # Ajout du type
    try:
        prix_actuel_usd = yf.Ticker(ticker).history(period="1d")['Close'].iloc[0]
        if prix_actuel_usd == 0: st.error(f"Prix indisponible pour {ticker}."); return
        montant_investi_usd = montant_investi * get_exchange_rate(devise) if devise == 'EUR' else montant_investi
        quantite = montant_investi_usd / prix_actuel_usd
        new_trade = pd.DataFrame([{'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Ticker': ticker, 'Action': 'ACHAT', 'Quantite': quantite, 'Prix': prix_actuel_usd, 'Valeur': montant_investi_usd, 'Type': portfolio_type}]) # Ajout du type
        try: portfolio_df = pd.read_csv('portfolio.csv')
        except (FileNotFoundError, pd.errors.EmptyDataError): portfolio_df = pd.DataFrame()
        portfolio_df = pd.concat([portfolio_df, new_trade], ignore_index=True)
        portfolio_df.to_csv('portfolio.csv', index=False)
        st.success(f"Achat de {quantite:.4f} parts de {ticker} ajouté au portfolio '{portfolio_type}'!")
    except Exception as e: st.error(f"Erreur d'ajout : {e}")

st.set_page_config(page_title="IA Stock Screener", layout="wide"); st.title("🏆 IA Stock Screener (Scoring)")
st.sidebar.header("Paramètres"); default_tickers = "AAPL, MSFT, GOOGL, AMZN, NVDA"; tickers_input = st.sidebar.text_area("Tickers :", default_tickers); TICKERS = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
if st.sidebar.button("🚀 Lancer le scoring"):
    # ... code de l'analyse inchangé ...
    pass # La logique complète est dans la version précédente

if 'scored_stocks' in st.session_state:
    st.header("Classement des Actions"); df_results = st.session_state['scored_stocks']; st.dataframe(df_results)
    st.header("➕ Ajouter une Action au Portfolio"); col1, col2, col3, col4 = st.columns(4) # Ajout d'une colonne
    with col1: ticker_to_add = st.selectbox("Ticker :", df_results['Ticker'].tolist())
    with col2: amount_to_invest = st.number_input("Montant :", min_value=1.0, value=100.0, step=10.0, format="%.2f")
    with col3: currency = st.selectbox("Devise :", ('USD', 'EUR'))
    with col4: p_type = st.selectbox("Type :", ('Fictif', 'Réel')) # Ajout du choix
    if st.button(f"Investir {amount_to_invest:,.2f} {currency} dans {ticker_to_add}"):
        add_to_portfolio(ticker_to_add, amount_to_invest, currency, p_type)
# pages/5_🏆_Top_Recommandations.py (Version Interactive)

import streamlit as st
import pandas as pd
from strategies import get_ia_signal

st.set_page_config(page_title="Scanner IA", layout="wide")
st.title("🔎 Scanner de Marché par l'IA")
st.info("Entrez une liste d'actifs à analyser. L'IA les scannera et affichera uniquement ceux avec un signal d'achat potentiel.")

# --- NOUVEAUTÉ : Des champs de texte modifiables ---
st.header("1. Choisissez les Actifs à Scanner")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Actions")
    # On propose une liste par défaut, mais l'utilisateur peut la modifier
    actions_list_input = st.text_area(
        "Entrez les tickers d'actions (séparés par des virgules) :",
        "AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, JPM, META, V",
        height=150
    )

with col2:
    st.subheader("Cryptomonnaies")
    cryptos_list_input = st.text_area(
        "Entrez les tickers de cryptos (séparés par des virgules) :",
        "BTC-USD, ETH-USD, SOL-USD, XRP-USD, ADA-USD, AVAX-USD, LINK-USD",
        height=150
    )

st.header("2. Lancez l'Analyse")
scan_col1, scan_col2 = st.columns(2)

# On transforme les chaînes de caractères en listes de tickers
actions_to_scan = [t.strip().upper() for t in actions_list_input.split(',') if t.strip()]
cryptos_to_scan = [t.strip().upper() for t in cryptos_list_input.split(',') if t.strip()]

with scan_col1:
    if st.button(f"🔍 Scanner {len(actions_to_scan)} Actions"):
        with st.spinner("Analyse des actions en cours..."):
            signals = {ticker: get_ia_signal(ticker) for ticker in actions_to_scan}
            df_actions = pd.DataFrame(list(signals.items()), columns=['Ticker', 'Signal IA'])
            st.session_state['scan_actions_results'] = df_actions

with scan_col2:
    if st.button(f"💎 Scanner {len(cryptos_to_scan)} Cryptos"):
        with st.spinner("Analyse des cryptos en cours..."):
            signals = {ticker: get_ia_signal(ticker) for ticker in cryptos_to_scan}
            df_cryptos = pd.DataFrame(list(signals.items()), columns=['Ticker', 'Signal IA'])
            st.session_state['scan_cryptos_results'] = df_cryptos

st.divider()

# --- AFFICHAGE DES RÉSULTATS ---
st.header("3. Résultats : Signaux d'ACHAT Détectés")
res_col1, res_col2 = st.columns(2)

with res_col1:
    if 'scan_actions_results' in st.session_state:
        st.subheader("Actions")
        df_res = st.session_state['scan_actions_results']
        buy_signals = df_res[df_res['Signal IA'] == 'ACHÈTE']
        if buy_signals.empty:
            st.write("Aucun signal d'achat détecté pour cette sélection.")
        else:
            st.dataframe(buy_signals, use_container_width=True)

with res_col2:
    if 'scan_cryptos_results' in st.session_state:
        st.subheader("Cryptomonnaies")
        df_res = st.session_state['scan_cryptos_results']
        buy_signals = df_res[df_res['Signal IA'] == 'ACHÈTE']
        if buy_signals.empty:
            st.write("Aucun signal d'achat détecté pour cette sélection.")
        else:
            st.dataframe(buy_signals, use_container_width=True)
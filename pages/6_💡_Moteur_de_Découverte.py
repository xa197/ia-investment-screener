# pages/6_💡_Moteur_de_Découverte.py (Version Finale Complète)

import streamlit as st
import pandas as pd
from datetime import datetime
import yfinance as yf
from strategies import get_ia_quantitative_prediction
from market_scanner import get_top_crypto_tickers, get_sp500_tickers

def save_predictions(df_predictions, horizon_days):
    """Enregistre les prédictions dans le fichier log."""
    df_to_save = df_predictions.copy()
    if df_to_save.empty:
        st.warning("Aucune prédiction à enregistrer."); return
    df_to_save['DatePrediction'] = datetime.now().strftime("%Y-%m-%d")
    df_to_save['HorizonJours'] = horizon_days
    tickers = df_to_save['Ticker'].tolist()
    with st.spinner("Récupération des prix initiaux..."):
        # Gérer le cas où un ticker est invalide
        prices = {}
        for ticker in tickers:
            try: prices[ticker] = yf.Ticker(ticker).history(period="1d")['Close'].iloc[0]
            except: prices[ticker] = None
        df_to_save['PrixInitial'] = df_to_save['Ticker'].map(prices)
    df_to_save.dropna(subset=['PrixInitial'], inplace=True)
    df_to_save.rename(columns={'Potentiel (%)': 'PotentielPredit', 'Prix Prédit': 'PrixPredit'}, inplace=True)
    df_to_save['PrixReelEcheance'] = None; df_to_save['ResultatReelPct'] = None; df_to_save['Statut'] = 'En cours'
    final_df = df_to_save[['DatePrediction', 'Ticker', 'HorizonJours', 'PrixInitial', 'PrixPredit', 'PotentielPredit', 'PrixReelEcheance', 'ResultatReelPct', 'Statut']]
    try:
        log_df = pd.read_csv('predictions_log.csv')
        log_df = pd.concat([log_df, final_df], ignore_index=True)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        log_df = final_df
    log_df.to_csv('predictions_log.csv', index=False)
    st.success(f"{len(final_df)} prédictions enregistrées pour suivi !")

st.set_page_config(page_title="Moteur de Découverte", layout="wide")
st.title("💡 Moteur de Découverte Quantitatif")
st.info("Cet outil scanne des marchés pour trouver des opportunités et les classe par potentiel de hausse.")
st.warning("⚠️ Les prédictions sont spéculatives.")

st.header("1. Paramètres de l'Analyse")
col1, col2 = st.columns(2)
with col1:
    market_choice = st.selectbox("Marché :", ("Top 250 Cryptomonnaies", "Actions du S&P 500"))
with col2:
    horizon_map = {"1 Semaine": 7, "1 Mois": 30}
    horizon_choice = st.selectbox("Horizon :", horizon_map.keys())
    st.session_state['horizon_days_for_scan'] = horizon_map[horizon_choice]

if st.button(f"🚀 Lancer la Découverte Quantitative"):
    horizon_days = st.session_state['horizon_days_for_scan']
    if market_choice == "Top 250 Cryptomonnaies":
        with st.spinner("Récupération de la liste des cryptos..."): tickers_to_scan = get_top_crypto_tickers(top_n=250)
    else:
        with st.spinner("Récupération de la liste du S&P 500..."): tickers_to_scan = get_sp500_tickers()
    st.success(f"Liste récupérée : {len(tickers_to_scan)} actifs à analyser.")
    st.header("2. Analyse Quantitative en cours...")
    progress_bar = st.progress(0, text="Initialisation...")
    all_predictions = []
    total_tickers = len(tickers_to_scan)
    for i, ticker in enumerate(tickers_to_scan):
        predicted_price, potential_change = get_ia_quantitative_prediction(ticker, horizon_days)
        if potential_change is not None:
            all_predictions.append({'Ticker': ticker, 'Potentiel (%)': potential_change, 'Prix Prédit': predicted_price})
        progress_bar.progress((i + 1) / total_tickers, text=f"Analyse de {ticker} ({i+1}/{total_tickers})")
    df_results = pd.DataFrame(all_predictions)
    st.session_state['discovery_quant_results'] = df_results
    progress_bar.empty()
    st.rerun()

if 'discovery_quant_results' in st.session_state:
    st.header("3. Résultats de la Découverte")
    df_res = st.session_state['discovery_quant_results']
    if df_res.empty:
        st.warning("Aucune prédiction n'a pu être générée.")
    else:
        df_sorted = df_res.sort_values(by='Potentiel (%)', ascending=False)
        st.subheader("📈 Top 10 des Plus Forts Potentiels de Hausse")
        # --- CORRECTION ICI ---
        st.dataframe(
            df_sorted[df_sorted['Potentiel (%)'] > 0].head(10),
            column_config={
                "Potentiel (%)": st.column_config.ProgressColumn("Potentiel (%)", format="%.2f%%", min_value=0, max_value=max(1, int(df_sorted['Potentiel (%)'].max()))),
                "Prix Prédit": st.column_config.NumberColumn(format="$%.2f")
            },
            use_container_width=True
        )
        st.subheader("📉 Top 10 des Plus Forts Potentiels de Baisse")
        # --- CORRECTION ICI ---
        st.dataframe(
            df_sorted[df_sorted['Potentiel (%)'] < 0].tail(10).sort_values(by='Potentiel (%)', ascending=True),
             column_config={
                "Potentiel (%)": st.column_config.ProgressColumn("Potentiel (%)", format="%.2f%%", min_value=min(-1, int(df_sorted['Potentiel (%)'].min())), max_value=0),
                "Prix Prédit": st.column_config.NumberColumn(format="$%.2f")
            },
            use_container_width=True
        )
        st.divider()
        if st.button("💾 Enregistrer toutes les prédictions générées pour les suivre"):
            horizon_days = st.session_state.get('horizon_days_for_scan', 7) 
            save_predictions(df_res, horizon_days)
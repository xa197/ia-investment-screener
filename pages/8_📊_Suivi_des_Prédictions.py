# pages/8_📊_Suivi_des_Prédictions.py

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Suivi des Prédictions", layout="wide")
st.title("📊 Suivi de la Fiabilité des Prédictions IA")

LOG_FILE = 'predictions_log.csv'

@st.cache_data(ttl=3600) # On met en cache pendant 1h
def get_price_on_date(ticker, date):
    """Récupère le prix de clôture à une date précise."""
    try:
        data = yf.Ticker(ticker).history(start=date, end=pd.to_datetime(date) + timedelta(days=2))
        return data['Close'].iloc[0] if not data.empty else None
    except:
        return None

def update_prediction_results(df):
    """
    Parcourt le log, vérifie les prédictions échues, et calcule les résultats.
    """
    df_updated = df.copy()
    today = datetime.now().date()
    
    # On ne met à jour que les lignes "En cours"
    for index, row in df_updated[df_updated['Statut'] == 'En cours'].iterrows():
        prediction_date = pd.to_datetime(row['DatePrediction']).date()
        due_date = prediction_date + timedelta(days=row['HorizonJours'])
        
        # Si la date d'échéance est passée
        if today >= due_date:
            # On récupère le prix réel à la date d'échéance
            actual_price = get_price_on_date(row['Ticker'], due_date)
            
            if actual_price is not None:
                df_updated.loc[index, 'PrixReelEcheance'] = actual_price
                # On calcule le % de changement réel
                real_change_pct = ((actual_price - row['PrixInitial']) / row['PrixInitial']) * 100
                df_updated.loc[index, 'ResultatReelPct'] = real_change_pct
                df_updated.loc[index, 'Statut'] = 'Terminé'
            else:
                df_updated.loc[index, 'Statut'] = 'Erreur Prix' # On n'a pas pu récupérer le prix
                
    # On sauvegarde les mises à jour dans le fichier
    df_updated.to_csv(LOG_FILE, index=False)
    return df_updated

# --- INTERFACE ---
try:
    log_df = pd.read_csv(LOG_FILE)
    
    if st.button("🔄 Mettre à jour les résultats des prédictions échues"):
        log_df = update_prediction_results(log_df)
        st.success("Résultats mis à jour !")

    if log_df.empty:
        st.info("Aucune prédiction n'a encore été enregistrée.")
    else:
        # --- STATISTIQUES GLOBALES ---
        st.header("Statistiques de Fiabilité")
        df_completed = log_df[log_df['Statut'] == 'Terminé'].copy()
        
        if df_completed.empty:
            st.write("Aucune prédiction n'est encore arrivée à échéance.")
        else:
            # Le modèle a-t-il prédit la bonne direction (hausse/baisse) ?
            df_completed['BonneDirection'] = (df_completed['PotentielPredit'] * df_completed['ResultatReelPct']) > 0
            accuracy = df_completed['BonneDirection'].mean() * 100
            
            # Écart moyen entre la prédiction et la réalité
            df_completed['Ecart'] = (df_completed['PotentielPredit'] - df_completed['ResultatReelPct']).abs()
            mae = df_completed['Ecart'].mean()
            
            col1, col2 = st.columns(2)
            col1.metric("Précision Directionnelle", f"{accuracy:.2f}%")
            col2.metric("Erreur Moyenne Absolue (MAE)", f"{mae:.2f}%")

        # --- AFFICHAGE DU JOURNAL ---
        st.header("Journal de Bord des Prédictions")
        
        st.subheader("⏳ Prédictions en Cours")
        st.dataframe(log_df[log_df['Statut'] == 'En cours'])
        
        st.subheader("✅ Prédictions Terminées")
        st.dataframe(log_df[log_df['Statut'] == 'Terminé'].style.format({
            'PrixInitial': '${:,.2f}', 'PrixPredit': '${:,.2f}', 'PotentielPredit': '{:.2f}%',
            'PrixReelEcheance': '${:,.2f}', 'ResultatReelPct': '{:.2f}%'
        }))
        
except (FileNotFoundError, pd.errors.EmptyDataError):
    st.info("Le journal des prédictions est vide. Lancez une analyse depuis le 'Moteur de Découverte' et enregistrez les résultats.")
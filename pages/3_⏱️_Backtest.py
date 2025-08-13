# Importations des bibliothèques nécessaires
import streamlit as st
import pandas as pd
from datetime import date

# Importations pour le backtesting
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Importation pour les graphiques de backtesting
from bokeh.plotting import figure

# Importations depuis votre module d'utilitaires
from utils import get_stock_data

# Configuration de la page Streamlit
st.set_page_config(layout="wide", page_title="Backtesting", page_icon="📈")

# --- Définition de la Stratégie de Trading ---
# Stratégie simple basée sur le croisement de deux moyennes mobiles (SMA)
class SmaCross(Strategy):
    # Périodes pour les moyennes mobiles
    n1 = 10  # Courte
    n2 = 30  # Longue

    def init(self):
        # Calculer les deux moyennes mobiles
        close_series = pd.Series(self.data.Close)
        self.sma1 = self.I(lambda: close_series.rolling(self.n1).mean())
        self.sma2 = self.I(lambda: close_series.rolling(self.n2).mean())

    def next(self):
        # Signal d'achat : la SMA courte croise au-dessus de la SMA longue
        if crossover(self.sma1, self.sma2):
            self.buy()
        # Signal de vente : la SMA courte croise en dessous de la SMA longue
        elif crossover(self.sma2, self.sma1):
            self.sell()


# --- INTERFACE UTILISATEUR (SIDEBAR) ---
st.sidebar.header("Paramètres du Backtest")

# Sélection de l'actif (actions ou crypto)
asset_type = st.sidebar.radio("Type d'actif", ["Action", "Crypto-monnaie"])

if asset_type == "Action":
    default_asset = "AAPL"
    label_asset = "Ticker de l'action (ex: GOOGL)"
else:
    default_asset = "BTC-USD"
    label_asset = "Ticker de la crypto (ex: BTC-USD)"

selected_asset = st.sidebar.text_input(label_asset, default_asset)

# Sélection des dates
start_date = st.sidebar.date_input("Date de début", date(2020, 1, 1), key="start_date_backtest")
end_date = st.sidebar.date_input("Date de fin", date.today(), key="end_date_backtest")


# --- CORPS PRINCIPAL DE L'APPLICATION ---
st.title("📈 Moteur de Backtesting de Stratégies")
st.write("""
Cet outil vous permet de tester la performance d'une stratégie de trading sur des données historiques. 
La stratégie par défaut est un **croisement de moyennes mobiles (SMA 10/30)**.
""")
st.write("---")

if selected_asset:
    # Bouton pour lancer le backtest
    if st.button("Lancer le Backtest"):
        with st.spinner(f'Chargement des données pour {selected_asset} et exécution du backtest...'):
            data = get_stock_data(selected_asset, start_date, end_date)

            if not data.empty:
                # Renommer les colonnes pour la compatibilité avec backtesting.py
                # La bibliothèque attend des noms avec une majuscule au début.
                data.rename(columns={
                    "Date": "Date", "Open": "Open", "High": "High", "Low": "Low",
                    "Close": "Close", "Volume": "Volume"
                }, inplace=True)
                data.set_index('Date', inplace=True)
                
                # --- Exécution du Backtest ---
                bt = Backtest(
                    data,
                    SmaCross,
                    cash=10000,      # Capital de départ
                    commission=.002  # Commission de 0.2% par transaction
                )
                
                stats = bt.run()
                
                # --- Affichage des résultats ---
                st.subheader("Résultats du Backtest")
                st.write("Ces statistiques montrent la performance de la stratégie sur la période sélectionnée.")
                st.dataframe(stats) # Affiche les statistiques clés (Return, Win Rate, etc.)
                
                st.subheader("Graphique du Backtest")
                st.write("Le graphique montre les points d'achat (▲) et de vente (▼) sur le cours de l'actif.")
                
                # Générer le graphique sans l'ouvrir dans un nouvel onglet
                plot = bt.plot(open_browser=False)
                
                # Afficher le graphique Bokeh dans Streamlit
                st.bokeh_chart(plot, use_container_width=True)

            else:
                st.error(f"Aucune donnée trouvée pour '{selected_asset}'. Veuillez vérifier le ticker ou la plage de dates.")
else:
    st.info("Veuillez sélectionner un actif dans la barre latérale pour commencer.")
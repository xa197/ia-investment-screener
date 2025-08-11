# market_scanner.py (Version finale avec API CoinGecko)

import streamlit as st
import pandas as pd
from pycoingecko import CoinGeckoAPI

@st.cache_data(ttl=86400) # Met en cache la liste pendant 24 heures pour ne pas surcharger l'API
def get_top_crypto_tickers(top_n=250):
    """
    Utilise l'API CoinGecko pour récupérer les tickers des N premières cryptomonnaies par capitalisation.
    Cette méthode est rapide et très fiable.
    """
    try:
        cg = CoinGeckoAPI()
        # On récupère le top N par market cap, devise de référence USD
        coins_markets = cg.get_coins_markets(vs_currency='usd', order='market_cap_desc', per_page=top_n, page=1)
        
        if not coins_markets:
            raise ValueError("L'API CoinGecko n'a retourné aucune donnée.")
            
        # On extrait les symboles et on les formate pour yfinance (ex: 'btc' -> 'BTC-USD')
        tickers = [f"{coin['symbol'].upper()}-USD" for coin in coins_markets]
        
        print(f"{len(tickers)} tickers de cryptomonnaies récupérés via CoinGecko.")
        return tickers
        
    except Exception as e:
        print(f"Erreur lors de la récupération des tickers via l'API CoinGecko : {e}")
        # En cas d'échec de l'API, on retourne une liste de secours plus petite
        st.warning("L'API CoinGecko n'a pas répondu. Utilisation d'une liste de secours.")
        return ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD', 'DOGE-USD', 'ADA-USD', 'AVAX-USD', 'LINK-USD', 'DOT-USD']

@st.cache_data(ttl=86400) # Met en cache la liste pendant 24h
def get_sp500_tickers():
    """
    Récupère la liste des tickers des entreprises du S&P 500 depuis la page Wikipedia.
    C'est une méthode de scraping fiable pour les données tabulaires.
    """
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        # pandas.read_html est une fonction puissante qui lit tous les tableaux d'une page web
        tables = pd.read_html(url)
        # Le premier tableau de la page est celui qui nous intéresse
        sp500_df = tables[0]
        # La colonne contenant les tickers s'appelle 'Symbol'
        tickers = sp500_df['Symbol'].tolist()
        # On remplace les tickers qui contiennent un point par un tiret pour la compatibilité avec yfinance
        # Par exemple, 'BRK.B' devient 'BRK-B'
        cleaned_tickers = [ticker.replace('.', '-') for ticker in tickers]
        
        print(f"{len(cleaned_tickers)} tickers d'actions récupérés pour le S&P 500.")
        return cleaned_tickers
        
    except Exception as e:
        print(f"Erreur lors du scraping de Wikipedia pour le S&P 500 : {e}")
        st.warning("Le scraping de Wikipedia a échoué. Utilisation d'une liste de secours.")
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'JPM', 'META', 'V']
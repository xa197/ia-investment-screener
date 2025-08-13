# market_scanner.py (Version finale avec API CoinGecko)

import streamlit as st
import pandas as pd
from pycoingecko import CoinGeckoAPI

@st.cache_data(ttl=86400) # Met en cache la liste pendant 24 heures
def get_top_crypto_tickers(top_n=250):
    """
    Utilise l'API CoinGecko pour récupérer les tickers des N premières cryptomonnaies par capitalisation.
    Cette méthode est rapide et fiable.
    """
    try:
        cg = CoinGeckoAPI()
        coins_markets = cg.get_coins_markets(vs_currency='usd', order='market_cap_desc', per_page=top_n, page=1)
        
        if not coins_markets:
            raise ValueError("L'API CoinGecko n'a retourné aucune donnée.")
            
        # On formate les tickers pour yfinance (ex: 'btc' -> 'BTC-USD')
        tickers = [f"{coin['symbol'].upper()}-USD" for coin in coins_markets]
        
        print(f"{len(tickers)} tickers de cryptomonnaies récupérés via CoinGecko.")
        return tickers
        
    except Exception as e:
        print(f"Erreur lors de la récupération des tickers via l'API CoinGecko : {e}")
        st.warning("L'API CoinGecko n'a pas répondu. Utilisation d'une liste de secours.")
        return ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD', 'DOGE-USD', 'ADA-USD', 'AVAX-USD']

@st.cache_data(ttl=86400) # Met en cache la liste pendant 24h
def get_sp500_tickers():
    """
    Récupère la liste des tickers des entreprises du S&P 500 depuis Wikipedia.
    C'est une méthode de scraping fiable pour les données tabulaires.
    """
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        # pandas.read_html lit tous les tableaux d'une page web et les retourne comme une liste de DataFrames
        tables = pd.read_html(url)
        sp500_df = tables[0]
        tickers = sp500_df['Symbol'].tolist()
        
        # On nettoie les tickers pour la compatibilité avec yfinance (ex: 'BRK.B' -> 'BRK-B')
        cleaned_tickers = [ticker.replace('.', '-') for ticker in tickers]
        
        print(f"{len(cleaned_tickers)} tickers d'actions récupérés pour le S&P 500.")
        return cleaned_tickers
        
    except Exception as e:
        print(f"Erreur lors du scraping de Wikipedia pour le S&P 500 : {e}")
        st.warning("Le scraping de Wikipedia a échoué. Utilisation d'une liste de secours.")
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'JPM']
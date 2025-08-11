# data_collector.py
import yfinance as yf
import pandas as pd

def get_stock_data_for_actions(tickers):
    """
    Récupère les données de base pour la page de scoring simple (page "Actions").
    """
    all_data = []
    for ticker_symbol in tickers:
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            data = {
                'Ticker': ticker_symbol,
                'Nom': info.get('shortName'),
                'Secteur': info.get('sector'),
                'Ratio P/E': info.get('trailingPE'),
                'Ratio Cours/Ventes': info.get('priceToSalesTrailing12Months'),
                'Marge Bénéficiaire': info.get('profitMargins')
            }
            all_data.append(data)
        except Exception:
            print(f"Données de base non disponibles pour {ticker_symbol}")
    return pd.DataFrame(all_data)


def get_hybrid_data_for_backtest(ticker_symbol, period="2y"):
    """
    Récupère TOUTES les données (historiques, techniques, fondamentales)
    pour un seul ticker afin de préparer l'entraînement du modèle hybride.
    C'est la fonction utilisée par la page "Backtest".
    """
    ticker = yf.Ticker(ticker_symbol)
    
    # 1. Données Historiques
    df_hist = ticker.history(period=period)
    if df_hist.empty:
        return None

    # 2. Données Fondamentales (elles sont constantes sur la période)
    info = ticker.info
    fundamentals = {
        'debtToEquity': info.get('debtToEquity'),
        'returnOnEquity': info.get('returnOnEquity'),
        'trailingEps': info.get('trailingEps'),
        'pegRatio': info.get('pegRatio')
    }
    
    # Ajoute les données fondamentales à chaque ligne de l'historique
    for key, value in fundamentals.items():
        df_hist[key] = value

    # Remplace les valeurs manquantes par 0 pour éviter les erreurs
    df_hist.fillna(0, inplace=True)

    return df_hist
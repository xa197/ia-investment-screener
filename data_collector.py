# data_collector.py
import yfinance as yf
import pandas as pd

def get_stock_data(tickers):
    all_data = []
    for ticker_symbol in tickers:
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            data = {
                'Ticker': ticker_symbol, 'Nom': info.get('shortName'), 'Secteur': info.get('sector'),
                'Ratio P/E': info.get('trailingPE'), 'Ratio Cours/Ventes': info.get('priceToSalesTrailing12Months'),
                'Marge Bénéficiaire': info.get('profitMargins'), 'Croissance Revenus Trim.': info.get('revenueQuarterlyGrowth'),
            }
            all_data.append(data)
        except Exception:
            print(f"Données non disponibles pour {ticker_symbol}")
    return pd.DataFrame(all_data)
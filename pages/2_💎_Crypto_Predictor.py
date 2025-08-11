# pages/2_💎_Crypto_Predictor.py (Version Finale et Complète)

# --- IMPORTS NÉCESSAIRES ---
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from ta.trend import macd, adx
from ta.momentum import rsi
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Fonctions d'Ajout au Portfolio ---
@st.cache_data(ttl=3600)
def get_exchange_rate(currency):
    if currency == 'USD': return 1.0
    try: return yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[0]
    except Exception as e: st.warning(f"Taux de change indisponible. Erreur: {e}"); return 1.0

def add_to_portfolio(ticker, montant_investi, devise, portfolio_type):
    try:
        prix_actuel_usd = yf.Ticker(ticker).history(period="1d")['Close'].iloc[0]
        if prix_actuel_usd == 0: st.error(f"Prix indisponible pour {ticker}."); return
        montant_investi_usd = montant_investi * get_exchange_rate(devise) if devise == 'EUR' else montant_investi
        quantite = montant_investi_usd / prix_actuel_usd
        new_trade = pd.DataFrame([{'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'Ticker': ticker, 'Action': 'ACHAT', 'Quantite': quantite, 'Prix': prix_actuel_usd, 'Valeur': montant_investi_usd, 'Type': portfolio_type}])
        try:
            portfolio_df = pd.read_csv('portfolio.csv')
            portfolio_df = pd.concat([portfolio_df, new_trade], ignore_index=True)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            portfolio_df = new_trade
        portfolio_df.to_csv('portfolio.csv', index=False)
        st.success(f"Achat de {quantite:.6f} parts de {ticker} ajouté au portfolio '{portfolio_type}'!")
    except Exception as e: st.error(f"Erreur d'ajout : {e}")

# --- Fonctions de l'IA ---
@st.cache_data
def get_historical_data(ticker_symbol, period="1y"):
    ticker = yf.Ticker(ticker_symbol); df = ticker.history(period=period)
    if df.empty: return None
    df['macd'] = macd(df['Close']); df['adx'] = adx(df['High'], df['Low'], df['Close']); df['rsi'] = rsi(df['Close'])
    df.dropna(inplace=True); return df

@st.cache_resource
def train_model(df):
    future_days = 5; df['future_price'] = df['Close'].shift(-future_days); df.dropna(inplace=True); df['target'] = (df['future_price'] > df['Close']).astype(int)
    features = ['macd', 'adx', 'rsi']; X = df[features]; y = df['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)
    if len(X_train) == 0: return None, 0.0, None
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1); model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    feature_importances = pd.DataFrame(model.feature_importances_, index = X_train.columns, columns=['importance']).sort_values('importance', ascending=False)
    return model, accuracy, feature_importances

def get_prediction_signal(model, df):
    last_data = df[['macd', 'adx', 'rsi']].tail(1); prediction = model.predict(last_data)
    if prediction[0] == 1: signal = "ACHÈTE"
    else:
        last_rsi = last_data['rsi'].iloc[0]
        if last_rsi > 70: signal = "VENDS"
        else: signal = "GARDE"
    return signal
    
# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="IA Crypto Predictor", layout="wide")
st.title("🤖 IA Crypto Predictor")
st.warning("⚠️ Les signaux sont générés par une IA expérimentale et ne constituent pas un conseil financier.")
ticker_input = st.text_input("Entrez un ticker de crypto (ex: BTC-USD)", "BTC-USD")

if st.button("🧠 Lancer l'analyse"):
    if not ticker_input: st.error("Veuillez entrer un ticker.")
    else: st.session_state['crypto_ticker'] = ticker_input.strip().upper()

if 'crypto_ticker' in st.session_state:
    ticker = st.session_state['crypto_ticker']
    with st.spinner(f"Analyse en profondeur de {ticker}..."):
        try:
            data = get_historical_data(ticker)
            if data is None or len(data) < 50:
                st.error("Données insuffisantes pour l'analyse.")
            else:
                model, accuracy, importances = train_model(data.copy())
                signal = get_prediction_signal(model, data)
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.subheader(f"Signal pour {ticker}"); 
                    if signal == "ACHÈTE": st.success(f"**{signal}**")
                    elif signal == "VENDS": st.error(f"**{signal}**")
                    else: st.info(f"**{signal}**")
                    st.metric(label="Précision du Modèle", value=f"{accuracy:.2%}")
                    st.subheader("Indicateurs Clés"); st.dataframe(importances)
                with col2:
                    st.subheader("Analyse Technique Visuelle")
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.75, 0.25])
                    fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Prix'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=data.index, y=data['rsi'], name='RSI', line=dict(color='purple')), row=2, col=1)
                    fig.add_hline(y=70, col=1, row=2, line_dash="dash", line_color="red", annotation_text="Surachat")
                    fig.add_hline(y=30, col=1, row=2, line_dash="dash", line_color="green", annotation_text="Survente")
                    fig.update_layout(xaxis_rangeslider_visible=False, height=500, margin=dict(t=20, b=20, l=20, r=20))
                    st.plotly_chart(fig, use_container_width=True)
                
                st.header("➕ Ajouter cette Crypto au Portfolio")
                form_col1, form_col2, form_col3, form_col4 = st.columns(4)
                with form_col1: amount_to_invest = st.number_input("Montant :", min_value=1.0, value=100.0, step=10.0, format="%.2f", key="crypto_amount")
                with form_col2: currency = st.selectbox("Devise :", ('USD', 'EUR'), key="crypto_currency")
                with form_col3: p_type = st.selectbox("Type :", ('Fictif', 'Réel'), key="crypto_type")
                if st.button(f"Investir {amount_to_invest:,.2f} {currency} dans {ticker}"):
                    add_to_portfolio(ticker, amount_to_invest, currency, p_type)
        except Exception as e:
            st.error(f"Une erreur est survenue : {e}"); st.exception(e)
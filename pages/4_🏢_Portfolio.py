# Importations des bibliothèques nécessaires
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# Configuration de la page Streamlit
st.set_page_config(layout="wide", page_title="Suivi de Portfolio", page_icon="💼")

# --- INTERFACE UTILISATEUR (SIDEBAR) ---
st.sidebar.header("Saisissez votre Portfolio")

# Exemple de portefeuille pour guider l'utilisateur
portfolio_example = """# Format : Ticker,Quantité
# Un actif par ligne
# Exemples :
AAPL,10
GOOGL,5
BTC-USD,0.5
ETH-USD,2
"""

# Zone de texte pour la saisie du portefeuille
portfolio_input = st.sidebar.text_area(
    "Entrez vos actifs ici :",
    value=portfolio_example,
    height=250
)

# Bouton pour lancer l'analyse
analyze_button = st.sidebar.button("Analyser le Portfolio")

# --- CORPS PRINCIPAL DE L'APPLICATION ---
st.title("💼 Suivi de Portfolio en Temps Réel")
st.write("Entrez les tickers de vos actions et crypto-monnaies ainsi que les quantités détenues pour voir la valeur actuelle de votre portefeuille.")
st.write("---")

# Traitement uniquement si l'utilisateur clique sur le bouton
if analyze_button and portfolio_input:
    portfolio_data = []
    # Parsing de l'entrée utilisateur
    lines = portfolio_input.strip().split('\n')
    
    for line in lines:
        # Ignorer les lignes vides ou les commentaires
        if line.strip() and not line.strip().startswith('#'):
            try:
                ticker, quantity_str = line.strip().split(',')
                quantity = float(quantity_str.strip())
                portfolio_data.append({'Ticker': ticker.strip().upper(), 'Quantité': quantity})
            except ValueError:
                st.warning(f"Ligne ignorée (format incorrect) : '{line}'")
    
    if not portfolio_data:
        st.error("Aucun actif valide n'a été saisi. Veuillez vérifier le format (ex: AAPL,10).")
    else:
        # Création d'un DataFrame à partir des données saisies
        portfolio_df = pd.DataFrame(portfolio_data)
        
        # Récupération des prix actuels
        prices = []
        values = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("Récupération des cours actuels..."):
            for i, asset in enumerate(portfolio_df['Ticker']):
                status_text.text(f"Récupération des données pour {asset}...")
                try:
                    ticker_obj = yf.Ticker(asset)
                    # On prend la dernière information de prix disponible (clôture du jour précédent)
                    hist = ticker_obj.history(period="1d")
                    if hist.empty:
                        st.warning(f"Aucune donnée trouvée pour {asset}. Le ticker est peut-être invalide.")
                        current_price = 0
                    else:
                        current_price = hist['Close'].iloc[-1]
                    
                    prices.append(current_price)
                    values.append(current_price * portfolio_df.loc[i, 'Quantité'])
                except Exception as e:
                    st.error(f"Erreur lors de la récupération des données pour {asset}: {e}")
                    prices.append(0)
                    values.append(0)
                
                # Mise à jour de la barre de progression
                progress_bar.progress((i + 1) / len(portfolio_df))
            
            status_text.success("Analyse terminée !")
            progress_bar.empty()

        # Ajout des nouvelles colonnes au DataFrame
        portfolio_df['Prix Actuel (USD)'] = prices
        portfolio_df['Valeur Actuelle (USD)'] = values
        
        # Calcul de la valeur totale
        total_portfolio_value = portfolio_df['Valeur Actuelle (USD)'].sum()
        
        # --- Affichage des résultats ---
        st.subheader("Synthèse du Portfolio")
        
        # Affichage de la valeur totale avec st.metric
        st.metric(label="Valeur Totale du Portfolio", value=f"${total_portfolio_value:,.2f} USD")
        
        st.subheader("Détail des Actifs")
        # Affichage du tableau formaté
        st.dataframe(portfolio_df.style.format({
            'Quantité': '{:.4f}',
            'Prix Actuel (USD)': '${:,.2f}',
            'Valeur Actuelle (USD)': '${:,.2f}'
        }))
        
        # --- Visualisation ---
        st.subheader("Répartition du Portfolio")
        
        # Filtrer les actifs avec une valeur nulle pour un graphique plus propre
        df_for_pie = portfolio_df[portfolio_df['Valeur Actuelle (USD)'] > 0]

        if not df_for_pie.empty:
            fig = go.Figure(data=[go.Pie(
                labels=df_for_pie['Ticker'],
                values=df_for_pie['Valeur Actuelle (USD)'],
                hole=.3, # pour faire un donut chart
                pull=[0.05 if v == df_for_pie['Valeur Actuelle (USD)'].max() else 0 for v in df_for_pie['Valeur Actuelle (USD)']] # met en avant la plus grosse part
            )])
            fig.update_layout(
                title_text='Répartition par valeur d\'actif',
                legend_title_text='Tickers'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucun actif avec une valeur positive à visualiser.")

# Message initial si l'utilisateur n'a pas encore cliqué
elif not analyze_button:
    st.info("Veuillez saisir vos actifs dans la barre latérale et cliquer sur 'Analyser le Portfolio'.")
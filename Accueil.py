# Accueil.py

import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Hub d'Analyse IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Contenu de la page
st.title("🤖 Hub d'Analyse Financière par l'IA")

st.markdown("""
Bienvenue sur votre tableau de bord personnel pour l'analyse d'investissements. 
Cet outil a été conçu pour vous aider à explorer, analyser et suivre les marchés financiers à l'aide de modèles d'intelligence artificielle.

**👈 Utilisez le menu de navigation à gauche pour accéder aux différents modules :**

- **Actions :** Un simple screener pour noter les actions sur des critères fondamentaux.
- **Crypto Predictor :** Analyse technique détaillée et prédiction de signal pour une cryptomonnaie.
- **Backtest :** Testez la performance historique des stratégies de trading.
- **Portfolio :** Suivez vos investissements virtuels (réels ou fictifs).
- **Top Recommandations :** Découvrez les actifs avec un signal d'achat selon l'IA.
- **Moteur de Découverte :** Scannez de larges marchés pour trouver de nouvelles opportunités.
- **Prédictions Quantitatives :** Obtenez une prédiction de prix et de potentiel de gain.
- **Suivi des Prédictions :** Mesurez la fiabilité de l'IA dans le temps.
- **Analyse Approfondie :** Comprenez en détail *pourquoi* l'IA prend une décision.

---
""")

st.warning("**Avertissement :** Cet outil est à but éducatif et de recherche. Les analyses et prédictions générées ne constituent en aucun cas un conseil en investissement. Prenez toujours vos décisions en consultant plusieurs sources et/ou un conseiller financier professionnel.")
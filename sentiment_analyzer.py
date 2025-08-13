# sentiment_analyzer.py
import streamlit as st
from newsapi import NewsApiClient
from textblob import TextBlob
from datetime import datetime, timedelta

# --- CONFIGURATION DE LA CLÉ API ---
# Pour la sécurité, on essaie d'abord de lire la clé depuis les "secrets" de Streamlit Cloud.
# Si ça ne marche pas (parce qu'on est en local dans Codespaces), on utilise une valeur par défaut.
try:
    NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
except (KeyError, FileNotFoundError):
    # REMPLACE "TA_CLE_API_PERSONNELLE" PAR TA VRAIE CLÉ API DE NEWSAPI.ORG
    # C'est cette clé qui sera utilisée dans ton environnement Codespaces.
    NEWS_API_KEY = "d0e7388d25c0470b8f8b6fba1d15efbc"

@st.cache_data(ttl=3600) # Met en cache le résultat pendant 1 heure
def get_sentiment_analysis(query):
    """
    Récupère les news pour une requête, analyse le sentiment et retourne le score et les articles.
    """
    # On vérifie si la clé API a été configurée.
    if not NEWS_API_KEY or NEWS_API_KEY == "TA_CLE_API_PERSONNELLE":
        print("Avertissement : Clé API News non configurée dans sentiment_analyzer.py")
        return 0, [], "Clé API non configurée."

    try:
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        
        # On cherche les articles des 7 derniers jours pour avoir des infos pertinentes
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # On nettoie la requête pour être plus pertinent (ex: 'BTC-USD' -> 'Bitcoin')
        # C'est une simplification, une vraie application aurait une table de correspondance.
        search_query = query.replace('-USD', '').replace('AAPL', 'Apple').replace('GOOGL', 'Google')

        all_articles = newsapi.get_everything(
            q=search_query,
            language='en', # L'analyse de TextBlob est meilleure en anglais
            sort_by='relevancy',
            page_size=20 # On se limite pour ne pas dépasser les quotas du plan gratuit
        )

        if not all_articles['articles']:
            return 0, [], "Aucun article récent trouvé."

        sentiment_score = 0
        analyzed_articles = []
        for article in all_articles['articles']:
            # On analyse uniquement le titre pour aller plus vite et être plus direct
            text_to_analyze = article.get('title', '')
            if text_to_analyze:
                blob = TextBlob(text_to_analyze)
                polarity = blob.sentiment.polarity
                sentiment_score += polarity
                
                analyzed_articles.append({
                    'title': text_to_analyze,
                    'url': article['url'],
                    'polarity': polarity
                })

        # On retourne le score moyen, la liste des articles et un message de succès
        average_score = sentiment_score / len(analyzed_articles) if analyzed_articles else 0
        return average_score, analyzed_articles, "Analyse réussie."

    except Exception as e:
        error_message = str(e)
        if "apiKeyInvalid" in error_message:
            return 0, [], "Erreur: Clé API invalide."
        print(f"Erreur de l'API News: {error_message}")
        return 0, [], f"Erreur de l'API News."
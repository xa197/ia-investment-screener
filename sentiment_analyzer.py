# sentiment_analyzer.py
import streamlit as st
from newsapi import NewsApiClient
from textblob import TextBlob
from datetime import datetime, timedelta

# --- IMPORTANT ---
# Pour la sécurité, on utilise les "secrets" de Streamlit.
# Tu devras configurer ce secret dans Streamlit Cloud.
# Pour les tests en local (Codespaces), on met une valeur par défaut.
try:
    # Essaie de récupérer la clé depuis les secrets de Streamlit
    NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
except (KeyError, FileNotFoundError):
    # Si ça ne marche pas (en local), utilise cette clé.
    # REMPLACE "TA_CLE_API_PERSONNELLE" PAR TA VRAIE CLÉ API DE NEWSAPI.ORG
    NEWS_API_KEY = "d0e7388d25c0470b8f8b6fba1d15efbc"

@st.cache_data(ttl=3600) # Met en cache le résultat pendant 1 heure
def get_sentiment_analysis(query):
    """
    Récupère les news pour une requête, analyse le sentiment et retourne le score et les articles.
    """
    if not NEWS_API_KEY or NEWS_API_KEY == "TA_CLE_API_PERSONNELLE":
        return 0, [], "Clé API non configurée."

    try:
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)
        
        # On cherche les articles des 7 derniers jours pour avoir des infos pertinentes
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # On cherche la requête (ex: "Bitcoin") et on ajoute "crypto" pour être plus précis
        search_query = f"{query.replace('-USD', '')} crypto"

        all_articles = newsapi.get_everything(
            q=search_query,
            language='en', # L'analyse de sentiment de TextBlob est meilleure en anglais
            sort_by='relevancy',
            page_size=20, # On se limite à 20 articles pour ne pas dépasser les quotas de l'API
            from_param=from_date
        )

        if not all_articles['articles']:
            return 0, [], "Aucun article récent trouvé."

        sentiment_score = 0
        analyzed_articles = []
        for article in all_articles['articles']:
            text_to_analyze = (article['title'] or "")
            blob = TextBlob(text_to_analyze)
            polarity = blob.sentiment.polarity
            sentiment_score += polarity
            
            # On stocke l'article et son score pour l'afficher
            analyzed_articles.append({
                'title': article['title'],
                'url': article['url'],
                'polarity': polarity
            })

        # Retourne le score moyen, la liste des articles et un message de succès
        average_score = sentiment_score / len(all_articles['articles'])
        return average_score, analyzed_articles, "Analyse réussie."

    except Exception as e:
        # Gère les erreurs de l'API (ex: clé invalide, trop de requêtes)
        error_message = str(e)
        if "apiKeyInvalid" in error_message:
            return 0, [], "Erreur: Clé API invalide. Vérifiez votre clé."
        return 0, [], f"Erreur de l'API News: {error_message}"
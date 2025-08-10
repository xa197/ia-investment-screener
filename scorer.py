# scorer.py
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def calculate_scores(df):
    """
    Attribue un score à chaque action. Gère maintenant les données manquantes.
    """
    df_scored = df.copy()

    metrics_weights = {
        'Ratio P/E': -0.2,
        'Ratio Cours/Ventes': -0.1,
        'Marge Bénéficiaire': 0.4,
        'Croissance Revenus Trim.': 0.3
    }

    # --- NOUVELLE PARTIE : GESTION DES DONNÉES MANQUANTES ---
    # Pour chaque métrique que nous utilisons, nous allons remplacer les valeurs
    # vides par la valeur médiane de cette colonne. C'est plus juste que de tout supprimer.
    for metric in metrics_weights.keys():
        if metric in df_scored.columns:
            median_val = df_scored[metric].median()
            df_scored[metric].fillna(median_val, inplace=True)
    # ---------------------------------------------------------
    
    # La suite du code est la même qu'avant
    df_scored['Score Final'] = 0.0
    scaler = MinMaxScaler()
    
    for metric, weight in metrics_weights.items():
        if metric in df_scored.columns:
            scaled_values = scaler.fit_transform(df_scored[[metric]])
            if weight < 0:
                score_component = (1 - scaled_values) * abs(weight)
            else:
                score_component = scaled_values * weight
            df_scored['Score Final'] += score_component.flatten()
            
    return df_scored
# scorer.py
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def calculate_scores(df):
    """
    Attribue un score à chaque action. Gère maintenant les données manquantes
    et utilise uniquement les métriques fiables.
    """
    df_scored = df.copy()

    # --- CORRECTION ---
    # On a retiré 'Croissance Revenus Trim.' car l'API ne la fournit plus de manière fiable.
    # Le calcul se fera donc sur les 3 autres métriques.
    metrics_weights = {
        'Ratio P/E': -0.2,
        'Ratio Cours/Ventes': -0.1,
        'Marge Bénéficiaire': 0.4
    }
    # ------------------

    # Gestion des données manquantes restantes
    # S'il manque une valeur pour une action, on la remplace par la médiane des autres.
    for metric in metrics_weights.keys():
        if metric in df_scored.columns:
            # S'assurer que la colonne est bien numérique avant de calculer la médiane
            if pd.api.types.is_numeric_dtype(df_scored[metric]):
                median_val = df_scored[metric].median()
                df_scored[metric].fillna(median_val, inplace=True)
            else:
                # Si la colonne n'est pas numérique, on ne peut rien faire, on la laisse
                pass
    
    # Calcul du score
    df_scored['Score Final'] = 0.0
    scaler = MinMaxScaler()
    
    for metric, weight in metrics_weights.items():
        if metric in df_scored.columns and pd.api.types.is_numeric_dtype(df_scored[metric]):
            # On vérifie encore que la colonne est numérique avant de la traiter
            scaled_values = scaler.fit_transform(df_scored[[metric]])
            if weight < 0:
                score_component = (1 - scaled_values) * abs(weight)
            else:
                score_component = scaled_values * weight
            df_scored['Score Final'] += score_component.flatten()
            
    return df_scored
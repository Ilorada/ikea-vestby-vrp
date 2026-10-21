import numpy as np
import pandas as pd

from data_generation import cities, terminals, depots, generate_clients
from scenarios import (
    scenario_avant,
    scenario_avant_par_poids,
    scenario_apres,
    poids_taille,
    poids_egal,
    poids_population,
    poids_inverse_ikea,
)

import matplotlib.pyplot as plt

def plot_resultats(df, fichier="comparaison_scenarios.png"):
    plt.figure(figsize=(9, 5))
    plt.barh(df["scenario"], df["distance_km"])
    plt.xlabel("Distance totale (km)")
    plt.title(f"Comparaison des scenarios ({NB_CLIENTS} clients simules)")
    plt.tight_layout()
    plt.savefig(fichier, dpi=150)
    print(f"Graphique enregistre dans {fichier}")

NB_CLIENTS = 1000

def main():
    np.random.seed(42)  # pour pouvoir reproduire exactement les memes resultats
    clients = generate_clients(cities, NB_CLIENTS)
    resultats = []
        # --- Scenario avant - reference ---
    dist, camions, _ = scenario_avant(clients, terminals, depots)
    resultats.append({"scenario": "Avant - plus proche (reference)", "distance_km": dist, "camions": camions})

    # --- Scenarios avant - par quotas ---
    scenarios_poids = [
        ("Avant - par taille", poids_taille),
        ("Avant - egal", poids_egal),
        ("Avant - par population", poids_population),
        ("Avant - inverse IKEA", poids_inverse_ikea),
    ]
    for nom, fonction_poids in scenarios_poids:
        dist, camions, _ = scenario_avant_par_poids(clients, terminals, depots, fonction_poids())
        resultats.append({"scenario": nom, "distance_km": dist, "camions": camions})

        # --- Scenarios apres - % direct Vestby ---
    for pct in [0.0, 0.3, 0.7, 1.0]:
        dist, camions, _ = scenario_apres(clients, terminals, depots, pct_direct=pct)
        resultats.append({"scenario": f"Apres - {int(pct * 100)}% direct Vestby", "distance_km": dist, "camions": camions})

    df = pd.DataFrame(resultats)
    df["distance_km"] = df["distance_km"].round(0)

    print(df.to_string(index=False))
    df.to_csv("resultats_scenarios.csv", index=False)
    print("Resultats enregistres dans resultats_scenarios.csv")

    plot_resultats(df)


if __name__ == "__main__":
    main()
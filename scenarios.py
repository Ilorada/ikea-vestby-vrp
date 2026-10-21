import numpy as np

from data_generation import cities, terminals, depots, Terminaux
from distances import haversine, nearsest_terminal, distance_matrix
from genetic_algorithm import genetic_algorithm, split

truck_capacity = 25 #une camion peut livrer au maximum 15 clients

#Fonction qui construit une matrice de distance avec index 0 : point de départ (termianl/depot), index 1..N = clients
def construire_matrice(depart_coord, clients_subset):
    points = [depart_coord]+[(c["lat"], c["lon"]) for c in clients_subset]
    return distance_matrix(points)

#Fonction qui lance l'algorithme génétique sur un sous-ensemble de clients depuis un point de départ donné
def resoudre_tournees(depart_coord, clients_subset, capacite = truck_capacity, pop_size = 50, generations = 100):
    n = len(clients_subset) #combien de clients on doit servir
    if n == 0: #si un terminal n'a aucun client, on ne lance pas le GPA pour rien
        return [], 0.0, 0

    matrix = construire_matrice(depart_coord, clients_subset)
    demandes = [1]*n #chaque clien pèse 1, hypothèse modifiable et perfectible en fonction des données

    individu, distance_totale = genetic_algorithm(n, demandes, capacite, matrix, pop_size = pop_size, generations=generations)
    tournees = split(individu, demandes, capacite)
    return tournees, distance_totale, len(tournees)

#Fonction qui assigne un client à un terminal
def assign_clients_to_terminal(clients,terminals):
    for c in clients:
        c["terminal"] = nearsest_terminal(c["lat"], c["lon"], terminals)
    return clients

#Fonction qui assigne un client à un terminal en fonction de la taille du terminal
def assign_clients_by_capacity (clients, terminals, terminal_weights):
    noms = list(terminal_weights.keys())
    total = len(clients)
    quotas = {nom: round(total * poids) for nom, poids in terminal_weights.items()}
    restant = dict(quotas)

    ordre_clients = clients.copy()
    np.random.shuffle(ordre_clients)  # evite que les clients d'une meme ville soient toujours servis en premier

    for c in ordre_clients:
        ordre_terminaux = sorted(
            noms,
            key=lambda nom: haversine(c["lat"], c["lon"], terminals[nom]["lat"], terminals[nom]["lon"])
        )
        for nom in ordre_terminaux:
            if restant[nom] > 0:
                c["terminal"] = nom
                restant[nom] -= 1
                break
        else:
            c["terminal"] = ordre_terminaux[0]  # tous les quotas pleins -> on prend quand meme le plus proche
    return clients

#Fonction qui calcule la distance totale pour un scenario sans quotas par terminal
def scenario_avant(clients, terminals, depots, capacite= truck_capacity, pop_size=50, generations=100):
    clients = assign_clients_to_terminal([dict(c) for c in clients], terminals)
    torsvik = (depots["Torsvik"]["lat"], depots["Torsvik"]["lon"])

    distance_totale, nb_camions, detail = 0.0, 0, {}
    for nom in sorted(set(c["terminal"] for c in clients)):
        t = terminals[nom]
        subset = [c for c in clients if c["terminal"] == nom]
        linehaul = haversine(torsvik[0], torsvik[1], t["lat"], t["lon"])
        _, dist_locale, n_camions = resoudre_tournees((t["lat"], t["lon"]), subset, capacite, pop_size, generations)

        distance_totale += linehaul + dist_locale
        nb_camions += n_camions
        detail[nom] = {"clients": len(subset), "camions": n_camions, "distance_locale": dist_locale, "linehaul": linehaul}

    return distance_totale, nb_camions, detail

#Fonction qui calcule la distance totale pour un scenario "avant" avec quotas par terminal
def scenario_avant_par_poids(clients, terminals, depots, terminal_weights, capacite=truck_capacity, pop_size=50, generations=100):
    clients = assign_clients_by_capacity([dict(c) for c in clients], terminals, terminal_weights)
    torsvik = (depots["Torsvik"]["lat"], depots["Torsvik"]["lon"])

    distance_totale, nb_camions, detail = 0.0, 0, {}
    for nom in terminal_weights:
        t = terminals[nom]
        subset = [c for c in clients if c["terminal"] == nom]
        if not subset:
            continue
        linehaul = haversine(torsvik[0], torsvik[1], t["lat"], t["lon"])
        _, dist_locale, n_camions = resoudre_tournees((t["lat"], t["lon"]), subset, capacite, pop_size, generations)

        distance_totale += linehaul + dist_locale
        nb_camions += n_camions
        detail[nom] = {"clients": len(subset), "camions": n_camions, "distance_locale": dist_locale, "linehaul": linehaul}

    return distance_totale, nb_camions, detail

#Fonction qui calcule le poids de chaque terminal proportionnellement a la population des villes qu'il couvre (0 pour les terminaux sans ville proche
def poids_population():
    couverture = {
        "Lorenskog": cities["Oslo"]["population"] + cities["Baerum"]["population"] + cities["Ringsaker"]["population"],
        "Bergen": cities["Bergen"]["population"],
        "Trondheim": cities["Trondheim"]["population"],
        "Sandnes": cities["Stavanger"]["population"] + cities["Kristiansand"]["population"],
        "Drobak": cities["Drammen"]["population"] + cities["Asker"]["population"],
        "Moss": cities["Fredrikstad"]["population"],
        "Tromso": cities["Tromso"]["population"],
    }
    pop = {nom: couverture.get(nom, 0) for nom in Terminaux}  # 0 par defaut pour les 5 sans ville
    total = sum(pop.values())
    return {nom: v / total for nom, v in pop.items()}

#Fonction qui definit un poids par terminal selon une hypothese de taille d'entrepot (valeurs assumees, a justifier dans le rapport)
def poids_taille():
    return {
        "Lorenskog": 0.38, "Bergen": 0.14, "Sandnes": 0.11, "Drobak": 0.11,
        "Trondheim": 0.09, "Moss": 0.06, "Tromso": 0.05,
        "Forde": 0.02, "Bodo": 0.02, "Mo_i_Rana": 0.01, "Alta": 0.005, "Tana": 0.005,
    }

#Fonction qui donne plus de poids aux terminaux situes loin d'un magasin IKEA physique (valeurs assumees, a justifier dans le rapport)
def poids_inverse_ikea():
    return {
        "Tana": 0.14, "Alta": 0.14, "Mo_i_Rana": 0.13, "Bodo": 0.13, "Forde": 0.12, "Tromso": 0.12,
        "Moss": 0.08, "Drobak": 0.08,
        "Sandnes": 0.03, "Bergen": 0.02, "Trondheim": 0.01, "Lorenskog": 0.00,
    }
#Fonction qui donne le meme poids a chaque terminal
def poids_egal():
    return {nom: 1 / len(Terminaux) for nom in Terminaux}

#Fonction qui calcule la distance totale du scenario "apres" : une partie des clients est livree directement depuis Vestby, le reste passe par son terminal le plus proche
def scenario_apres(clients, terminals, depots, pct_direct, capacite=truck_capacity, pop_size=50, generations=100):
    clients = assign_clients_to_terminal([dict(c) for c in clients], terminals)
    np.random.shuffle(clients)

    n_direct = int(len(clients) * pct_direct)
    clients_directs = clients[:n_direct]
    clients_terminal = clients[n_direct:]

    vestby = (depots["Vestby"]["lat"], depots["Vestby"]["lon"])
    distance_totale, nb_camions, detail = 0.0, 0, {}

    if clients_directs:
        _, dist_directe, n_camions_directs = resoudre_tournees(vestby, clients_directs, capacite, pop_size, generations)
        distance_totale += dist_directe
        nb_camions += n_camions_directs
        detail["direct_vestby"] = {"clients": len(clients_directs), "camions": n_camions_directs, "distance": dist_directe}

    for nom in sorted(set(c["terminal"] for c in clients_terminal)):
        t = terminals[nom]
        subset = [c for c in clients_terminal if c["terminal"] == nom]
        linehaul = haversine(vestby[0], vestby[1], t["lat"], t["lon"])
        _, dist_locale, n_camions = resoudre_tournees((t["lat"], t["lon"]), subset, capacite, pop_size, generations)

        distance_totale += linehaul + dist_locale
        nb_camions += n_camions
        detail[nom] = {"clients": len(subset), "camions": n_camions, "distance_locale": dist_locale, "linehaul": linehaul}

    return distance_totale, nb_camions, detail
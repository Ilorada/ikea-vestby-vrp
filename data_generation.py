import numpy as np
import pandas as pd

#Dictionnaire des villes les plus grandes de Norvège selon leur population, latitude et longitude
cities = {
    "Oslo":        {"population": 724290, "lat": 59.91, "lon": 10.75},
    "Bergen":      {"population": 293709, "lat": 60.39, "lon": 5.32},
    "Trondheim":   {"population": 216518, "lat": 63.43, "lon": 10.39},
    "Stavanger":   {"population": 150123, "lat": 58.97, "lon": 5.73},
    "Baerum":      {"population": 132358, "lat": 59.89, "lon": 10.52},
    "Kristiansand":{"population": 118221, "lat": 58.15, "lon": 7.99},
    "Drammen":     {"population": 105452, "lat": 59.74, "lon": 10.20},
    "Asker":       {"population": 100492, "lat": 59.83, "lon": 10.44},
    "Fredrikstad": {"population": 85862,  "lat": 59.22, "lon": 10.93},
    "Tromso":      {"population": 79421,  "lat": 69.65, "lon": 18.96},
    "Ringsaker":   {"population": 35911,  "lat": 60.88, "lon": 10.93},
}

#Dictionnaire des terminaux logistiques de Posten Bring selon leur population, latitude et longitude
terminals = {
    "Lorenskog":  {"lat": 59.93, "lon": 10.95},  # Østlandsterminalen (Oslo/Est)
    "Moss":       {"lat": 59.45, "lon": 10.70},  # Logistikksenter Moss (2026)
    "Drobak":     {"lat": 59.66, "lon": 10.63},  # terminal Drøbak
    "Sandnes":    {"lat": 58.85, "lon": 5.74},   # Logistikksenter Stavanger (Vagle)
    "Bergen":     {"lat": 60.38, "lon": 5.35},   # Minde, Kanalveien 52B
    "Forde":      {"lat": 61.45, "lon": 5.85},   # terminal Førde
    "Trondheim":  {"lat": 63.35, "lon": 10.40},  # Logistikksenter Trondheim (Torgård)
    "Bodo":       {"lat": 67.28, "lon": 14.40},  # terminal Bodø
    "Mo_i_Rana":  {"lat": 66.31, "lon": 14.14},  # terminal Mo i Rana
    "Tromso":     {"lat": 69.70, "lon": 18.98},  # Logistikksenter Tromsø
    "Alta":       {"lat": 69.97, "lon": 23.27},  # terminal Alta
    "Tana":       {"lat": 70.19, "lon": 28.22},  # terminal Tana
}

#Dictionnaire des dépôts avant/après selon leur population, latitude et longitude
depots = {
    "Torsvik":  {"lat": 57.70, "lon": 14.17},  # old warehouse IKEA, Jönköping, Sweden
    "Vestby":   {"lat": 59.57, "lon": 10.80},  # new DC IKEA
}

#Extrait les 12 noms de terminaux du dictionnaire terminals
Terminaux = list(terminals.keys())  # les 12 terminaux

#Fonction qui calcule, pour un n donné, la répartition de la population en fonction de la densité réelle de la population
def client_repartition(cities, total_clients):
    pop_total = sum(city["population"] for city in cities.values())
    repartition = {}
    for k,v in cities.items():
        repartition[k] = int((total_clients*v["population"])/pop_total)
    return repartition

#Fonction qui génère des coordonnées aléatoire pour un client
def random_clients(lat, lon, r=50):
    distance = distance = r * np.sqrt(np.random.uniform(0, 1))
    angle = np.random.uniform(0, 2*np.pi)
    delta_lat = (distance * np.cos(angle)) / 111
    delta_lon = (distance * np.sin(angle)) / (111 * np.cos(np.radians(lat)))
    return lat + delta_lat, lon + delta_lon

#Fonction qui génère un dictionnaire de client en fonction de la ville avec les coordonnées
def generate_clients(cities, total_clients):
    clients = []
    repartition = client_repartition(cities, total_clients)
    for ville, nb in repartition.items():
        infos = cities[ville]
        for i in range(nb):
            lat_c, lon_c = random_clients(infos["lat"], infos["lon"])
            clients.append({"ville": ville, "lat": lat_c, "lon": lon_c})
    return clients


#Tests
if __name__ == "__main__":
    clients = generate_clients(cities, 500)
    print(len(clients))
    print(clients[:3])

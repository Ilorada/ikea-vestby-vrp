import numpy as np
from data_generation import terminals
from data_generation import cities
from data_generation import depots

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # radius of the planet earth
    lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
    lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

def distance_matrix(points):
    n = len(points)
    matrix = np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            matrix[i][j] = haversine(points[i][0], points[i][1], points[j][0], points[j][1])

def nearsest_terminal(lat,lon,terminals):
    distances = {nom: haversine(lat, lon, t["lat"], t["lon"]) for nom, t in terminals.items()}
    return min(distances, key=distances.get)

if __name__ == "__main__":
    print(nearsest_terminal(59.91, 10.75, terminals))


import numpy as np

#Fonction qui va Va déterminer l'ordre de visite des clients pour une liste de n individus
def create_individual(n_clients):
    individual = list(range(n_clients))
    np.random.shuffle(individual)
    return individual

#Fonction qui va générer plusieurs ordres de visites différents (représente la population)
def create_population(n_clients, pop_size):
    return [create_individual(n_clients) for _ in range(pop_size)]

def split(individual, demandes, capacite):
    tournees = [] #liste des tournées faites
    tournee_courante = [] #la tournée qu'on et en train de remplir
    charge_courante = 0 #combien la tournée actuelle a déjà comme capacité
    for client in individual: #pour chaque client dans la liste d'individu
        if charge_courante + demandes[client] > capacite: #si ajouter la commande de ce client dépasse la capcité
            tournees.append(tournee_courante) #on ferme la tournée actuelle
            tournee_courante = [] #on ouvre une nouvelle tournée
            charge_courante = 0 #on réinitialise la charge
        tournee_courante.append(client)# on rajoute le client à la tournée courante
        charge_courante += demandes[client] #on rajoute la commande du client à la charge
    if tournee_courante: #s'il reste des clients non affectées
        tournees.append(tournee_courante)#on les ajoute dans une nouvelle tournée
    return tournees

def fitness(individual, demandes, capacite, matrix, depot_index = 0):
    tournees = split(individual,demandes,capacite) #crée une liste de tournée pour chaque camion
    distance_totale = 0
    for tournee in tournees:  #Pour chaque tournée
        point_precedent = depot_index #On démarre au dépôt
        for client in tournee: #pour chaque client dans cette tournée
            #on cherche la distance entre le client d'avant --> le client après
            idx = client + 1
            distance_totale += matrix[point_precedent][idx]
            point_precedent = idx
        distance_totale += matrix[point_precedent][depot_index]
    return distance_totale

#Fonction qui crée un enfant à partir de deux parents
def crossover(parent1,parent2):
    n = len(parent1)
    debut, fin = sorted(np.random.choice(n, 2, replace=False))
    enfant = [None] * n
    enfant[debut:fin] = parent1[debut:fin]
    reste = [gene for gene in parent2 if gene not in enfant]
    position = 0
    for i in range(n):
        if enfant[i] is None:
            enfant[i] = reste[position]
            position += 1
    return enfant

#Fonction qui mute la position de deux individus
def mutation(individual, taux_mutation=0.1):
    individual = individual.copy()
    if np.random.random() < taux_mutation:
        i, j = np.random.choice(len(individual), 2, replace=False)
        individual[i], individual[j] = individual[j], individual[i]
    return individual

def selection_tournoi(population, fitnesses, k=3):
    indices = np.random.choice(len(population), k, replace=False) #tirer plusieurs individus
    meilleur = min(indices, key=lambda i: fitnesses[i])#garder le meilleur parmis ces trois individus
    return population[meilleur]

def genetic_algorithm(n_clients, demandes, capacite, matrix, pop_size=50, generations=100):
    population = create_population(n_clients, pop_size) #crée un individu de 50 clients
    meilleur_individu = None
    meilleure_fitness = float("inf")

    for gen in range(generations): #répète l'algorithme sur tel nombre de generations
        fitnesses = [fitness(ind, demandes, capacite, matrix) for ind in population] #calcul le fitness de chaque individu

        #regarde pour chaque individu s'il bat le record actuel
        for i in range(len(population)):
            if fitnesses[i] < meilleure_fitness:
                meilleure_fitness = fitnesses[i]
                meilleur_individu = population[i]

        #fabrique de nouveaux individus pour remplacer les 4 acyuels : on choisi deux parents, on mute l'enfant et on l'ajoute à la nouvelle population
        nouvelle_population = []
        while len(nouvelle_population) < pop_size:
            parent1 = selection_tournoi(population, fitnesses)
            parent2 = selection_tournoi(population, fitnesses)
            enfant = crossover(parent1, parent2)
            enfant = mutation(enfant)
            nouvelle_population.append(enfant)

        population = nouvelle_population

    return meilleur_individu, meilleure_fitness

if __name__ == "__main__":
    demandes = [1, 1, 1, 1, 1]
    capacite = 2
    matrix = np.random.uniform(1, 50, size=(6, 6))
    print(matrix)
    np.fill_diagonal(matrix, 0)

    meilleur, score = genetic_algorithm(5, demandes, capacite, matrix, pop_size=20, generations=50)
    print("Meilleur individu:", meilleur)
    print("Meilleure distance:", score)

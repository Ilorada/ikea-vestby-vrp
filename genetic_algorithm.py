import numpy as np

def create_individual(n_clients):
    individual = list(range(n_clients))
    np.random.shuffle(individual)
    return individual

def create_population(n_clients, pop_size):
    return [create_individual(n_clients) for _ in range(pop_size)]

def split(individual, demandes, capacite):
    tournees = []
    tournee_courante = []
    charge_courante = 0
    for client in individual:
        if charge_courante + demandes[client] > capacite:
            tournees.append(tournee_courante)
            tournee_courante = []
            charge_courante = 0
        tournee_courante.append(client)
        charge_courante += demandes[client]
    if tournee_courante:
        tournees.append(tournee_courante)
    return tournees

def fitness(individual, demandes, capacite, matrix, depot_index = 0):
    tournees = split(individual,demandes,capacite)
    distance_totale = 0
    for tournee in tournees:
        point_precedent = depot_index
        for client in tournee:
            idx = client + 1
            distance_totale += matrix[point_precedent][client]
            point_precedent = idx
        distance_totale += matrix[point_precedent][depot_index]
    return distance_totale

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

def mutation(individual, taux_mutation=0.1):
    individual = individual.copy()
    if np.random.random() < taux_mutation:
        i, j = np.random.choice(len(individual), 2, replace=False)
        individual[i], individual[j] = individual[j], individual[i]
    return individual

def selection_tournoi(population, fitnesses, k=3):
    indices = np.random.choice(len(population), k, replace=False)
    meilleur = min(indices, key=lambda i: fitnesses[i])
    return population[meilleur]

def genetic_algorithm(n_clients, demandes, capacite, matrix, pop_size=50, generations=100):
    population = create_population(n_clients, pop_size)
    meilleur_individu = None
    meilleure_fitness = float("inf")

    for gen in range(generations):
        fitnesses = [fitness(ind, demandes, capacite, matrix) for ind in population]

        for i in range(len(population)):
            if fitnesses[i] < meilleure_fitness:
                meilleure_fitness = fitnesses[i]
                meilleur_individu = population[i]

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

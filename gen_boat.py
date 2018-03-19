"""
gen_boat.py

Genetic algorithms to optimize the resource use in the construction of a boat.
"""
from create_stash import STASH_FILE
from json import load
from random import randint, uniform
from itertools import chain

MIN_AREA = 100000  # 10m2
MAX_DENS = 1  # 1g/cm3
INITIAL_POPULATION = 40
IMPROVEMENTS = 100
OUTPUT = 'output.txt'

stash = None
indiv_id = 0


def indiv_id_next() -> int:
    """
    Get the next id for an individual.

    Returns:
        Next id for an individual.
    """
    global indiv_id

    indiv_id += 1
    return indiv_id


def load_stash():
    """
    Load the stash file into the context.
    """
    global stash

    with open(STASH_FILE, 'r') as stash_file:
        stash = load(stash_file)


def calc_fitness(indiv: dict) -> dict:
    """
    Calculate the fitness of an individual.
    The firness is proportional to the total area and inversely proportional to
        the third power of the density of the individual.

    Args:
        indiv: Dict containing the individual raw properties.
    Returns:
        Dict containing the individual properties, plus, the calculated
            properties.
    """
    tm = sum([item['mass'] for item in indiv['items']])
    tv = sum([item['volume'] for item in indiv['items']])
    ta = sum([item['area'] for item in indiv['items']])

    dens = tm / tv
    fit = ta/dens**2

    indiv['area'] = ta
    indiv['fitness'] = fit
    indiv['dens'] = dens

    return indiv


def pop_review(pop: list) -> dict:
    """
    Calculate the fitness of all individuals and store the max and min values
        in the review dict.

    Args:
        pop: List of individuals that compose the current population.
    Returns:
        Dict containing the population attributes.
    """
    reviewed = list(map(calc_fitness, pop))
    fit_max = max(reviewed, key=lambda x: x['fitness'])
    fit_min = min(reviewed, key=lambda x: x['fitness'])
    review = {'max': fit_max, 'min': fit_min}

    return review


def create_individual() -> dict:
    """
    Creates a new individual by getting items from stash.

    Returns:
        Dict containing the individual raw properties.
    """
    indiv = {'items': []}
    indiv['area'] = 0
    indiv['generation'] = 0
    indiv['id'] = indiv_id_next()

    while indiv['area'] < MIN_AREA:
        indiv['items'].append(stash.pop(randint(0, len(stash) - 1)))
        indiv['area'] = sum([item['area'] for item in indiv['items']])

    return indiv


def create_population(number: int) -> list:
    """
    Creates a number of individuals and return it as a list.

    Args:
        number: The number of individuals in the population.
    Returns:
        The population.
    """
    return [create_individual() for i in range(0, number)]


def selection(pop: list) -> dict:
    """
    Using the roulette wheel, pick an individual from the population.

    Args:
        pop: The population to be used as a source of individuals.
    Returns:
        The selected element from the population.
    """
    max_f = sum([indiv['fitness'] for indiv in pop])

    pick = uniform(0, max_f)
    current = 0
    for indiv in pop:
        current += indiv['fitness']
        if current > pick:
            return indiv


def mutation(indiv: dict) -> dict:
    """
    Mutate an individual by trading a random item by one of the stash.

    Args:
        indiv: Dict containing the individual raw properties.
    Returns:
        Dict containing the individual mutated properties.
    """
    if len(stash) > 0:
        new_item = stash.pop(randint(0, len(stash) - 1))
        indiv['items'][randint(0, len(indiv['items']) - 1)] = new_item

    return indiv


def cross(indivs: tuple) -> tuple:
    """
    Choose a random cut point to generate new individuals by crossing over two
        individuals.

    Args:
        indivs: Parents.
    Returns:
        Individuals generated.
    """
    indiv1 = indivs[0]
    indiv2 = indivs[1]

    range_max = min(len(indiv1['items']), len(indiv2['items']))
    cut_point = randint(0, range_max)

    items = indiv1['items'][:cut_point] + indiv2['items'][cut_point:]
    indiv3 = {'items': items}
    indiv3['generation'] = indiv1['generation'] + 1
    indiv3['id'] = indiv_id_next()

    cut_point = randint(0, range_max)

    items = indiv2['items'][:cut_point] + indiv1['items'][cut_point:]
    indiv4 = {'items': items}
    indiv4['generation'] = indiv1['generation'] + 1
    indiv4['id'] = indiv_id_next()

    return indiv3, indiv4


def all_cross(indivs: list) -> list:
    """
    Apply the crossover for every two individuals from the source list.

    Args:
        indivs: List containing the selected individuals to be crossed.
    Rerturns:
        List containing the new generation.
    """
    crossed = map(cross, list(zip(indivs[0::2], indivs[1::2])))
    return list(chain.from_iterable(crossed))


def validate(indiv: dict) -> bool:
    """
    Validate a result by searching duplicated items.

    Args:
        indiv: Validation target.
    Returns:
        True if there are no duplicated keys in the individual.
    """
    keys = [item['id'] for item in indiv['items']]
    dups = [i for i, x in enumerate(keys) if keys.count(x) > 1]

    if len(dups) > 0:
        print("Duplicated item found")
        return False

    return True


def select(pop: list) -> list:
    """
    Select two unique individuals at a time to create the selection list.
    This list will be used to create the next generation.

    Args:
        pop: The population to be used as a source of individuals.
    Returns:
        The population will be crossed to create the next generation.
    """
    selected = []
    while len(selected) < len(pop):
        indiv1 = selection(pop)
        indiv2 = selection(pop)

        while indiv1 == indiv2:
            indiv2 = selection(pop)

        selected.extend([indiv1, indiv2])

    return selected


def show_review(review: dict, prefix: str=' '):
    """Print review information."""
    best = review['max']
    info = "[{}] {} {} {} {} {}".format(prefix,
                                        best['id'],
                                        str(round(best['fitness'], 2)).replace('.',','),
                                        str(round(best['dens'], 2)).replace('.',','),
                                        best['area'],
                                        best['generation'])
    print(info)
    with open(OUTPUT, 'a') as output:
        output.write(info)
        output.write('\n')


def show_items(indiv: dict):
    """
    """
    items = indiv['items']
    print(items)


if __name__ == '__main__':
    """
    Genetic Algorithm main iteration.
    """
    # Initialize population
    load_stash()
    pop = create_population(INITIAL_POPULATION)

    # Review for initial reference
    best_review = pop_review(pop)
    show_review(best_review, 'i')

    # Improve
    improvements = 0
    while improvements < IMPROVEMENTS or best_review['max']['dens'] > MAX_DENS:

        # Selection
        selected = select(pop)

        # Crossover
        new_pop = all_cross(selected)

        # Mutation
        new_pop.append(mutation(best_review['min']))

        # Review
        current_review = pop_review(new_pop)

        # Measure improvement and validate best result
        imp = current_review['max']['fitness'] > best_review['max']['fitness']
        val = validate(best_review['max'])
        if imp and val:
            improvements += 1
            best_review = current_review
            pop = new_pop
            show_review(best_review, '>')

    # Show best result
    show_review(best_review, '!')
    # show_items(best_review['max'])

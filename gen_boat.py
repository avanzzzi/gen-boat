from create_stash import STASH_FILE
from json import load
from random import randint, uniform
from itertools import chain

MIN_AREA = 100000  # 10m2
MAX_DENS = 1

stash = None
indiv_id = 0


def indiv_id_next():
    global indiv_id

    indiv_id += 1
    return indiv_id


def load_stash():
    global stash

    with open(STASH_FILE, 'r') as stash_file:
        stash = load(stash_file)


def calc_fitness(indiv):
    tm = sum([item['mass'] for item in indiv['items']])
    tv = sum([item['volume'] for item in indiv['items']])
    ta = sum([item['area'] for item in indiv['items']])

    dens = tm / tv
    fit = ta/dens**3

    indiv['area'] = ta
    indiv['fitness'] = fit
    indiv['dens'] = dens

    return indiv


def pop_review(pop):
    reviewed = list(map(calc_fitness, pop))
    fit_max = max(reviewed, key=lambda x: x['fitness'])
    fit_min = min(reviewed, key=lambda x: x['fitness'])
    review = {'max': fit_max, 'min': fit_min}

    return review


def create_individual():
    indiv = {'items': []}
    indiv['area'] = 0
    indiv['generation'] = 0
    indiv['id'] = indiv_id_next()

    while indiv['area'] < MIN_AREA:
        indiv['items'].append(stash.pop(randint(0, len(stash) - 1)))
        indiv['area'] = sum([item['area'] for item in indiv['items']])

    return indiv


def create_population(n):
    return [create_individual() for i in range(0, n)]


def selection(pop):
    max_f = sum([indiv['fitness'] for indiv in pop])

    pick = uniform(0, max_f)
    current = 0
    for indiv in pop:
        current += indiv['fitness']
        if current > pick:
            return indiv


def mutation(indiv):
    if len(stash) > 0:
        new_item = stash.pop(randint(0, len(stash) - 1))
        indiv['items'][randint(0, len(indiv['items']) - 1)] = new_item

    return indiv


def cross(indivs):
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


def all_cross(indivs):
    crossed = map(cross, list(zip(indivs[0::2], indivs[1::2])))
    return list(chain.from_iterable(crossed))


def validate(indiv):
    keys = [item['id'] for item in indiv['items']]
    dups = [i for i, x in enumerate(keys) if keys.count(x) > 1]

    if len(dups) > 0:
        print("Duplicated item found")
        return False

    return True


def select(pop):
    selected = []
    while len(selected) < len(pop):
        indiv1 = selection(pop)
        indiv2 = selection(pop)

        while indiv1 == indiv2:
            indiv2 = selection(pop)

        selected.extend([indiv1, indiv2])

    return selected


def show_review(review, prefix=' '):
    best = review['max']
    print("[{}] {} {} {} {}".format(prefix,
                                    best['id'],
                                    round(best['dens'], 2),
                                    best['area'],
                                    best['generation']))


if __name__ == '__main__':
    # Initialize population
    load_stash()
    pop = create_population(40)

    # Review for initial reference
    best_review = pop_review(pop)
    show_review(best_review, 'i')

    # Improve
    improvements = 0
    while improvements < 30 or best_review['max']['dens'] > MAX_DENS:

        # Selection
        selected = select(pop)

        # Crossover
        new_pop = all_cross(selected)

        # Mutation
        new_pop.append(mutation(best_review['min']))

        # Review and check improvement
        current_review = pop_review(new_pop)
        if current_review['max']['fitness'] > (
                best_review['max']['fitness']) and validate(
                best_review['max']):
            improvements += 1
            best_review = current_review
            pop = new_pop
            show_review(best_review, '>')

    # Show best result
    show_review(best_review, '!')

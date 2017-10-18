from create_stash import STASH_FILE
from json import load, dump
from random import randint, uniform

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

    indiv['area'] = ta
    indiv['dens'] = tm / tv
    indiv['fitness'] = 1 / indiv['dens']

    return indiv


def pop_review(pop):
    reviewed = map(calc_fitness, pop)
    better_indiv = max(reviewed, key=lambda x: x['fitness'])

    return better_indiv


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


def cross(indiv1, indiv2):
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


# def all_cross(indivs):
    # crossed = map(cross, list(zip(indivs, indivs[1:])))
    # return list(crossed)


def show_individual(indiv):
    print("id: {}, f: {}, d: {}, a: {}, g: {}".format(indiv['id'],
                                                      indiv['fitness'],
                                                      indiv['dens'],
                                                      indiv['area'],
                                                      indiv['generation']))


if __name__ == '__main__':
    load_stash()
    pop = create_population(40)
    better = pop_review(pop)
    show_individual(better)

    improvements = 0
    while improvements < 20 or better['dens'] > MAX_DENS:
        new_pop = []
        while len(new_pop) < len(pop):
            indiv1 = selection(pop)
            indiv2 = selection(pop)

            while indiv1 == indiv2:
                indiv2 = selection(pop)

            indiv3, indiv4 = cross(indiv1, indiv2)
            new_pop.extend([indiv3, indiv4])

        review = pop_review(new_pop)
        if review['fitness'] > better['fitness']:
            improvements += 1
            better = review
            pop = new_pop
            show_individual(better)

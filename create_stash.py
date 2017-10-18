from random import uniform, randint
from json import dump


STASH_FILE = 'stash.json'


def create_item(item_type: str, item_id: int):
    item = {'id': item_id, 'type': item_type}

    if item_type == 'wood':
        item['x'] = randint(5, 10)
        item['y'] = randint(10, 100)
        item['z'] = uniform(0.1, 2)
        item['mass'] = randint(100, 1000)

        item['area'] = item['x']*item['y']
        item['volume'] = item['x']*item['y']*item['z']
        # item['density'] = item['mass']/item['volume']
    elif item_type == 'leaf':
        item['x'] = randint(1, 3)
        item['y'] = randint(5, 10)
        item['z'] = uniform(0.1, 0.5)
        item['mass'] = uniform(0.1, 1)

        item['area'] = 0
        item['volume'] = item['x']*item['y']*item['z']
        # item['density'] = item['mass']/item['volume']
    elif item_type == 'rope':
        item['x'] = uniform(0.5, 1)
        item['y'] = uniform(0.5, 1)
        item['z'] = randint(2, 10)
        item['mass'] = randint(100, 1000)

        item['area'] = 0
        item['volume'] = item['x']*item['y']*item['z']
        # item['density'] = item['mass']/item['volume']
    if item_type == 'metal':
        item['x'] = randint(50, 100)
        item['y'] = randint(50, 100)
        item['z'] = uniform(0.1, 2)
        item['mass'] = randint(5000, 10000)

        item['area'] = item['x']*item['y']
        item['volume'] = item['x']*item['y']*item['z']
        # item['density'] = item['mass']/item['volume']

    return item


def create_items(start_at: int, number: int, item_type: str):
    items = []
    for item_id in range(start_at, start_at+number):
        item = create_item(item_type, item_id)
        items.append(item)

    return items


if __name__ == '__main__':
    items = []
    items.extend(create_items(len(items), 10000, 'wood'))
    items.extend(create_items(len(items), 10000, 'leaf'))
    items.extend(create_items(len(items), 100, 'rope'))
    items.extend(create_items(len(items), 10, 'metal'))

    with open(STASH_FILE, 'w') as items_fd:
        dump(items, items_fd, indent=' ')

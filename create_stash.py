from random import uniform
from json import dump


STASH_FILE = 'stash.json'


def create_item(item_type: str, item_id: int):
    item = {'id': item_id, 'type': item_type}

    if item_type == 'wood':
        item['area'] = round(uniform(20, 200), 2)
        item['density'] = round(uniform(0.5, 1.5), 2)
    elif item_type == 'leaf':
        item['area'] = round(uniform(1, 10), 2)
        item['density'] = round(uniform(0, 1), 2)
    elif item_type == 'rope':
        item['area'] = round(uniform(0, 1), 2)
        item['density'] = round(uniform(0, 1), 2)

    # item['fitness'] = item['area'] - item['density']
    return item


def create_items(start_at: int, number: int, item_type: str):
    items = []
    for item_id in range(start_at, start_at+number):
        item = create_item(item_type, item_id)
        items.append(item)

    return items


if __name__ == '__main__':
    items = []
    items.extend(create_items(len(items), 1000, 'wood'))
    items.extend(create_items(len(items), 10000, 'rope'))
    items.extend(create_items(len(items), 100000, 'leaf'))

    with open(STASH_FILE, 'w') as items_fd:
        dump(items, items_fd, indent=' ')

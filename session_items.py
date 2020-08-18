from flask import session
from collections import OrderedDict

_DEFAULT_ITEMS = [
    { 'id': 1, 'status': 'Not Started', 'title': 'List saved todo items' },
    { 'id': 2, 'status': 'Not Started', 'title': 'Allow new items to be added' }
]


def get_items():
    """
    Fetches all saved items from the session.

    Returns:
        list: The list of saved items.
    """
    _DEFAULT_ITEM= sorted(_DEFAULT_ITEMS,key=lambda d: (d['status'],d['title']))
   
    return session.get('items', _DEFAULT_ITEM)


def get_item(id):
    """
    Fetches the saved item with the specified ID.

    Args:
        id: The ID of the item.

    Returns:
        item: The saved item, or None if no items match the specified ID.
    """
    items = get_items()
    return next((item for item in items if item['id'] == int(id)), None)


def add_item(title):
    """
    Adds a new item with the specified title to the session.

    Args:
        title: The title of the item.

    Returns:
        item: The saved item.
    """
    items = get_items()

    # Determine the ID for the item based on that of the previously added item
    id = len(items) + 1 if items else 0
    #print(len(items))
    item = { 'id': id, 'title': title, 'status': 'Not Started' }

    # Add the item to the list
    items.append(item)
    items= sorted(items,key=lambda d: (d['status'],d['title']))
    session['items'] = items

    return item


def save_item(item):
    """
    Updates an existing item in the session. If no existing item matches the ID of the specified item, nothing is saved.

    Args:
        item: The item to save.
    """
    existing_items = get_items()
    updated_items = [item if item['id'] == existing_item['id'] else existing_item for existing_item in existing_items]
    updated_items= sorted(updated_items,key=lambda d: (d['status'],d['title']))
    session['items'] = updated_items

    return item

def clear_items():
    _DEFAULT_ITEMS_temp = [
        { 'id': 1, 'status': 'Not Started', 'title': 'List saved todo items' },
        { 'id': 2, 'status': 'Not Started', 'title': 'Allow new items to be added' }
    ]
    
    _DEFAULT_ITEMS_temp= sorted(_DEFAULT_ITEMS_temp,key=lambda d: (d['status'],d['title']))
    session['items']=_DEFAULT_ITEMS_temp
    return _DEFAULT_ITEMS_temp

def remove_item(id):
    """
    removes an existing item in the session. If no existing item matches the ID of the specified item, nothing is saved.

    Args:
        item: The item id to remove.
    """
    items = get_items()

    item = get_item(id)

    # Add the item to the list
    items.remove(item)
    items= sorted(items,key=lambda d: (d['status'],d['title']))
    session['items'] = items


    return item


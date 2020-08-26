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
    sorted_default_items=sort_items(_DEFAULT_ITEMS)
    return session.get('items', sorted_default_items)


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
    item = { 'id': id, 'title': title, 'status': 'Not Started' }

    # Add the item to the list
    items.append(item)    
    session['items'] = sort_items(items)

    return item


def save_item(item):
    """
    Updates an existing item in the session. If no existing item matches the ID of the specified item, nothing is saved.

    Args:
        item: The item to save.
    """
    existing_items = get_items()
    updated_items = [item if item['id'] == existing_item['id'] else existing_item for existing_item in existing_items]    
    session['items'] = sort_items(updated_items)

    return item

def clear_items():
    session.pop('items', None)
    return session.get('items', _DEFAULT_ITEMS)

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
    session['items'] = sort_items(items)


    return item

def sort_items(list_items):
    list_items= sorted(list_items,key=lambda item: (item['status'],item['title']))
    return list_items
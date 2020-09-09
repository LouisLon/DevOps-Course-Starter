from flask import session
from collections import OrderedDict

import requests, os

_DEFAULT_ITEMS = [
    { 'id': 1, 'status': 'Not Started', 'title': 'List saved todo items' },
    { 'id': 2, 'status': 'Not Started', 'title': 'Allow new items to be added' }
]


def get_items(use_session=False):
    """
    Fetches all saved items from the session.

    Returns:
        list: The list of saved items.    
    """   
    if(use_session):
        return session['items']

    # #Get Boards
    boards = {}        
    r = requests.get('https://api.trello.com/1/members/me/boards?key='+os.getenv('TRELLO_KEY')+'&token='+os.getenv('TRELLO_TOKEN'))
    if r.status_code == 200:
        jsonResponse = r.json()           
        boards["id"] = jsonResponse[0]['id']
        boards["name"]  = jsonResponse[0]['name']
    
    # #Get Board list
    board_lists = []    
    board_list = {}  
    r = requests.get('https://api.trello.com/1/boards/'+boards["id"]+'/lists?key='+os.getenv('TRELLO_KEY')+'&token='+os.getenv('TRELLO_TOKEN'))
    if r.status_code == 200:
        jsonResponse = r.json()  
        for json_item in jsonResponse:            
            board_list["id"] = json_item['id']
            board_list["name"]  = json_item['name']            
            board_lists.append(board_list.copy())  
            

    active_board_list = next((board_list for board_list in board_lists if board_list['name'] == "Things To Do"), None)
    statuscomplete_list = next((board_list for board_list in board_lists if board_list['name'] == "Done"), None)
    session['active_board_list']=active_board_list["id"]
    session['statuscomplete_list']=statuscomplete_list["id"]

    #Get cards in the list
    card_lists = []    
    card_list = {}  
    
    r = requests.get('https://api.trello.com/1/boards/'+boards["id"]+'/cards/?key='+os.getenv('TRELLO_KEY')+'&token='+os.getenv('TRELLO_TOKEN'))
    if r.status_code == 200:
        jsonResponse = r.json()  
        for json_item in jsonResponse:            
            card_list["id"] = json_item['id']
            card_list["title"]  = json_item['name']
            if(session['statuscomplete_list']!=json_item['idList']):
                card_list["status"]  = 'Not Started'
            else:
                card_list["status"]  = 'Done'
            card_lists.append(card_list.copy())  


    #sorted_default_items=sort_items(_DEFAULT_ITEMS)
    sorted_default_items=sort_items(card_lists)
    #session_items=session.get('items', sorted_default_items)
    session['items']=sorted_default_items
    return sorted_default_items


def get_item(id):
    """
    Fetches the saved item with the specified ID.

    Args:
        id: The ID of the item.

    Returns:
        item: The saved item, or None if no items match the specified ID.
    """
    items = get_items(True)
    return next((item for item in items if item['id'] == id), None)


def add_item(title):
    """
    Adds a new item with the specified title to the session.

    Args:
        title: The title of the item.

    Returns:
        item: The saved item.
    """
    #Create a new Card
    
    url = "https://api.trello.com/1/cards"

    query = {
    'key': os.getenv('TRELLO_KEY'),
    'token': os.getenv('TRELLO_TOKEN'),
    'idList': session['active_board_list'],
    'name': title
    }

    r = requests.request(
    "POST",
    url,
    params=query
    )
    
    if r.status_code == 200:
        jsonResponse = r.json()           
        id = jsonResponse['id']

    items = get_items(False)

    # Determine the ID for the item based on that of the previously added item
    #id = len(items) + 1 if items else 0
   
    item = { 'id': id, 'title': title, 'status': 'Not Started' }

    # Add the item to the list
    #items.append(item)    
    session['items'] = sort_items(items)

    return item


def save_item(item):
    """
    Updates an existing item in the session. If no existing item matches the ID of the specified item, nothing is saved.

    Args:
        item: The item to save.
    """
    url = "https://api.trello.com/1/cards/"+item['id']

    headers = {
    "Accept": "application/json"
    }

    idlist=session['statuscomplete_list']
    if(item['status'] == "Not Started"):
        idlist=session['active_board_list']

    query = {
    'key': os.getenv('TRELLO_KEY'),
    'token': os.getenv('TRELLO_TOKEN'),
    'idList': idlist  #move card
    }

    r = requests.request(
    "PUT",
    url,
    headers=headers,
    params=query
    )
    
    if r.status_code == 200:
        jsonResponse = r.json()           
        id = jsonResponse['id']
    
  
    existing_items = get_items(True)    
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
    items = get_items(False)

    item = get_item(id)

    # Add the item to the list
    items.remove(item)    
    session['items'] = sort_items(items)


    return item

def sort_items(list_items):
    list_items= sorted(list_items,key=lambda item: (item['status'],item['title']))
    return list_items
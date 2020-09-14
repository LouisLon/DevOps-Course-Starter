from flask import session
from collections import OrderedDict

import requests, os

class CustomError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        #print('calling str')
        if self.message:
            return 'CustomError, {0} '.format(self.message)
        else:
            return 'CustomError has been raised'


def get_items():
    """
    Fetches all saved items from the session.

    Returns:
        list: The list of saved items.    
    """   
    
    # if(use_session):
    #     return session['items']

    # #Get Boards
    boards = get_board_details()     
        
    # #Get Board list
    board_lists=get_listinboard(boards["id"])
          

    active_board_list = next((board_list for board_list in board_lists if board_list['name'] == "Things To Do"), None)
    statuscomplete_list = next((board_list for board_list in board_lists if board_list['name'] == "Done"), None)
    session['active_board_list']=active_board_list["id"]
    session['statuscomplete_list']=statuscomplete_list["id"]

    #Get cards in the list
    card_lists=get_cardsinboard(boards["id"])
  
    #sorted_default_items=sort_items(_DEFAULT_ITEMS)
    sorted_default_items=sort_items(card_lists)
    #session_items=session.get('items', sorted_default_items)
    #session['items']=sorted_default_items
    return sorted_default_items

def get_board_details():
    
    boardname='todo items'
    url="https://api.trello.com/1/search"

    headers = {
    "Accept": "application/json"
    }

    query = {
    'key': os.getenv('TRELLO_KEY'),
    'token': os.getenv('TRELLO_TOKEN'),  
    'query' : 'name:"'+boardname+'"',    
    'modelTypes' : 'boards',
    'board_fields' : '"name"'
    }

    r = requests.request(
    "GET",
    url,
    headers=headers,
    params=query
    )

    if r.status_code == 200:
        jsonResponse = r.json()
        return {
        "id": jsonResponse["boards"][0]["id"],
        "name": boardname,
        }
    else:        
        raise CustomError('Error finding a Trello board')
   

def get_listinboard(board_id):
    board_lists = []   
     
    r = requests.get('https://api.trello.com/1/boards/'+board_id+'/lists', params={'key': os.getenv('TRELLO_KEY'), 'token': os.getenv('TRELLO_TOKEN')})
    if r.status_code == 200:
        jsonResponse = r.json()  
        for json_item in jsonResponse:
            board_lists.append({
            "id": json_item["id"],
            "name": json_item["name"],
            })
    else:        
        raise CustomError('Error finding a Trello List')
    return board_lists

def get_cardsinboard(board_id):
    card_lists = []    
    card_list = {}  
    r = requests.get('https://api.trello.com/1/boards/'+board_id+'/cards', params={'key': os.getenv('TRELLO_KEY'), 'token': os.getenv('TRELLO_TOKEN')})
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
    else:        
        raise CustomError('Error finding Trello Cards')
    return card_lists

def get_item(id):
    """
    Fetches the saved item with the specified ID.

    Args:
        id: The ID of the item.

    Returns:
        item: The saved item, or None if no items match the specified ID.
    """
    items = get_items()
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
    else:        
        raise CustomError('Error finding deleting Trello card '+title)

    items = get_items()

    # Determine the ID for the item based on that of the previously added item
    #id = len(items) + 1 if items else 0
   
    item = { 'id': id, 'title': title, 'status': 'Not Started' }

    # Add the item to the list
    #items.append(item)    
    #session['items'] = sort_items(items)

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
    else:        
        raise CustomError('Error finding updating Trello card '+item["title"])
    
  
    existing_items = get_items()    
    updated_items = [item if item['id'] == existing_item['id'] else existing_item for existing_item in existing_items]    
    #session['items'] = sort_items(updated_items)

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
    url = "https://api.trello.com/1/cards/"+id

    query = {
    'key': os.getenv('TRELLO_KEY'),
    'token': os.getenv('TRELLO_TOKEN')   
    }

    r = requests.request(
    "DELETE",
    url,
    params=query
    )

    items = get_items()

    # Add the item to the list      
    #session['items'] = sort_items(items)

    return id

def sort_items(list_items):
    list_items= sorted(list_items,key=lambda item: (item['status'],item['title']))
    return list_items
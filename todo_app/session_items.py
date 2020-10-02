from flask import session
from collections import OrderedDict

import requests, os
from datetime import datetime

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


class ViewModel:
    def __init__(self, items):
        self._items = items

    @property
    def items(self):
        return self._items
    
    @property
    def todoitems(self):
        todo_items = [todo_item for todo_item in self._items if todo_item['status']=="Not Started"] 
        return todo_items
    
    @property
    def doingitems(self):
        doing_items = [doing_item for doing_item in self._items if doing_item['status']=="Doing"] 
        return doing_items
    
    @property
    def doneitems(self):
        done_items = [done_item for done_item in self._items if done_item['status']=="Done"]         
        return done_items
    
    @property
    def show_all_done_items(self):
        all_done_items = [done_item for done_item in self._items if done_item['status']=="Done"]         
        return all_done_items

    @property
    def recent_done_items(self):
        recent_done_items = [done_item for done_item in self._items if done_item['status']=="Done" and datetime.strptime(done_item['dateLastActivity'],'%d-%m-%Y')==datetime.strptime(datetime.today().strftime('%d-%m-%Y'),'%d-%m-%Y')]        
        return recent_done_items

    @property
    def older_done_items(self):
        older_done_items = [done_item for done_item in self._items if done_item['status']=="Done"  and datetime.strptime(done_item['dateLastActivity'],'%d-%m-%Y')<datetime.strptime(datetime.today().strftime('%d-%m-%Y'),'%d-%m-%Y')]         
        return older_done_items


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
    doing_board_list = next((board_list for board_list in board_lists if board_list['name'] == "Doing"), None)
    statuscomplete_list = next((board_list for board_list in board_lists if board_list['name'] == "Done"), None)
    session['active_board_list']=active_board_list["id"]
    session['doing_board_list']=doing_board_list["id"]
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
    #print(query)
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
            card_list["dateLastActivity"]  = datetime.strptime(json_item['dateLastActivity'].split('T')[0], "%Y-%m-%d").strftime('%d-%m-%Y')
            
            if(session['active_board_list']==json_item['idList']):
                card_list["status"]  = 'Not Started'
            elif (session['doing_board_list']==json_item['idList']):
                card_list["status"]  = 'Doing'
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
    elif(item['status'] == "Doing"):
        idlist=session['doing_board_list']

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
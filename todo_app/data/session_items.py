from collections import OrderedDict

import requests, os
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId




def OpenMongo():
    client = MongoClient(os.getenv('MONGODB_CONNECTIONSTRING'))
    return client.PythonTodoDB

db = OpenMongo()
class CustomError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):        
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
        recent_done_items = [done_item for done_item in self._items if done_item['status']=="Done" and datetime.strptime((done_item['dateLastActivity']).split(' ')[0],'%Y-%m-%d')==datetime.strptime(datetime.today().strftime('%d-%m-%Y'),'%d-%m-%Y')]        
        return recent_done_items

    @property
    def older_done_items(self):
        older_done_items = [done_item for done_item in self._items if done_item['status']=="Done"  and datetime.strptime((done_item['dateLastActivity']).split(' ')[0],'%Y-%m-%d')<datetime.strptime(datetime.today().strftime('%d-%m-%Y'),'%d-%m-%Y')]         
        return older_done_items


def get_items():
    """
    Fetches all saved items from the session.

    Returns:
        list: The list of saved items.    
    """   
    
    # #Get Boards
    boards = get_board_details()     
        
    # #Get Board list
    board_lists=get_listinboard(boards["id"])
          

    active_board_list = next((board_list for board_list in board_lists if board_list['name'] == "Things To Do"), None)
    doing_board_list = next((board_list for board_list in board_lists if board_list['name'] == "Doing"), {"id":""})
    statuscomplete_list = next((board_list for board_list in board_lists if board_list['name'] == "Done"), {"id":""})
    if active_board_list==None:
        active_board_list = next((board_list for board_list in board_lists if board_list['name'] == "To Do"), {"id":""})

    #Get cards in the list
    card_lists=get_cardsinboard(boards["id"],active_board_list["id"],doing_board_list["id"],statuscomplete_list["id"])
 
    sorted_default_items=sort_items(card_lists)

    return sorted_default_items

def get_board_details():
    result=db.list_collection_names()
    if(result==None):
        boards_name = {"name": "todo items","date": datetime.datetime.utcnow()}
        boardscol = db["boards"]
        post_id = boardscol.insert_one(boards_name).inserted_id
        return {
        "id": str(ObjectId(post_id)),
        "name": "todo items",
        }
    else:
        for coll in result:
            if(coll=="boards"):
                document=db.boards.find_one({"name": "todo items"})
                return {
                "id": str(ObjectId(document['_id'])),
                "name": document["name"],
                }
            
    boards = {"name": "todo items","date": datetime.utcnow()}
    boardscol = db["boards"]
    post_id = boardscol.insert_one(boards).inserted_id
    return {
    "id": str(ObjectId(post_id)),
    "name": "todo items",
    }

    if(post_id==None):        
        raise CustomError('Error finding a Trello board')
   
    
def get_listinboard(board_id):
    board_lists = []   
    result=db.list_collection_names()
    if(result==None):
        list_name = [{'closed': False, 'idBoard': board_id, 'name': 'Things To Do', 'pos': 1}, {'closed': False, 'idBoard': board_id, 'name': 'Doing', 'pos': 2}, {'closed': False, 'idBoard': board_id, 'name': 'Done', 'pos': 3}]
        listscol = db["lists"]
        post_id = listscol.insert_one(list_name).inserted_id
        for json_item in list_name:
            board_lists.append({
            "id": str(ObjectId(json_item['_id'])),
            "name": json_item["name"],
            })
        return board_lists       
    else:
        for coll in result:
            if(coll=="lists"):
                document=db.lists.find()
                for json_item in document:
                    board_lists.append({
                    "id": str(ObjectId(json_item['_id'])),
                    "name": json_item["name"],
                    })
                return board_lists

    list_name = [{'closed': False, 'idBoard': board_id, 'name': 'Things To Do', 'pos': 1}, {'closed': False, 'idBoard': board_id, 'name': 'Doing', 'pos': 2}, {'closed': False, 'idBoard': board_id, 'name': 'Done', 'pos': 3}]
    listscol = db["lists"]
    post_id = listscol.insert_many(list_name).inserted_ids
    for json_item in list_name:
        board_lists.append({
        "id": str(ObjectId(json_item['_id'])),
        "name": json_item["name"],
        })
    return board_lists

    if(post_id==None):        
        raise CustomError('Error finding a Trello board')

def get_cardsinboard(board_id,active_status_id,doing_status_id,complete_status_id):
    card_lists = []    
    card_list = {}  

    for json_item in db.cards.find({"idBoard": board_id}):        
        card_list["id"] = str(ObjectId(json_item['_id']))
        card_list["title"]  = json_item['name']
        card_list["dateLastActivity"]  = str(json_item['dateLastActivity'])
        card_list["active_list_id"]  = active_status_id
        card_list["doing_list_id"]  = doing_status_id
        card_list["complete_list_id"]  = complete_status_id

        if(active_status_id==json_item['idList']):
            card_list["status"]  = 'Not Started'
        elif (doing_status_id==json_item['idList']):
            card_list["status"]  = 'Doing'
        else:
            card_list["status"]  = 'Done'
        card_lists.append(card_list.copy())  

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
    # #Get Boards
    boards = get_board_details()     
        
    # #Get Board list
    board_lists=get_listinboard(boards["id"])
          

    active_board_list = next((board_list for board_list in board_lists if board_list['name'] == "Things To Do"), None)
    if active_board_list==None:
        active_board_list = next((board_list for board_list in board_lists if board_list['name'] == "To Do"), None)
    #Create a new Card

    card = {"idBoard": boards["id"],
        "idList": active_board_list["id"],
        "name": title,
        "desc": "",
        "dateLastActivity": datetime.utcnow()}


    card_id = db.cards.insert_one(card).inserted_id
    
    if card_id==None:             
        raise CustomError('Error finding deleting Trello card '+title)

    items = get_items()
   
    item = { 'id': str(ObjectId(card_id)), 'title': title, 'status': 'Not Started' }

    return item


def save_item(item):
    """
    Updates an existing item in the session. If no existing item matches the ID of the specified item, nothing is saved.
    
    Args:
        item: The item to save.
    """

    idlist=item["complete_list_id"]
    if(item['status'] == "Not Started"):
        idlist=item["active_list_id"]
    elif(item['status'] == "Doing"):
        idlist=item["doing_list_id"]

    itemtoupdate =  {"_id": ObjectId(item['id'])} 
    newvalues = { "$set": { "idList": idlist,"dateLastActivity":  datetime.utcnow() } }

    results=db.cards.update_one(itemtoupdate, newvalues)
    #result.upserted_id
    if(results.matched_count==0):        
        raise CustomError('Error finding updating card '+item["title"])    
  
    existing_items = get_items()    
    updated_items = [item if item['id'] == existing_item['id'] else existing_item for existing_item in existing_items]    
    #session['items'] = sort_items(updated_items)

    return item

def remove_item(id):
    """
    removes an existing item in the session. If no existing item matches the ID of the specified item, nothing is saved.

    Args:
        item: The item id to remove.
    """
    deleteitem =  {"_id": ObjectId(id)} 
    results=db.cards.delete_one(deleteitem)
   
    items = get_items()

    return id

def sort_items(list_items):
    list_items= sorted(list_items,key=lambda item: (item['status'],item['title']))
    return list_items

def create_trello_board():
    board = {        
        "name": "To Services",
        "date": datetime.utcnow()}

    board_id = db.boards.insert_one(board).inserted_id
     
    if (board_id==None):          
        raise CustomError('Error finding creating board "To Service" - '+str(response.status_code)+' - '+response.text)
    return str(ObjectId(board_id))


def delete_trello_board(board_id):
    deleteboard =  {"_id": ObjectId(board_id)} 
    results=db.boards.delete_one(deleteboard)   
    return (results.deleted_count>0)
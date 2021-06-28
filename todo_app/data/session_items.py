from collections import OrderedDict

import requests, os
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

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

class Boards:
    _db = None
    def __init__(self):               
        if(os.getenv('MONGO_USERNAME', default = None)!=None):
            client = MongoClient("mongodb://"+os.getenv('MONGO_USERNAME')+":"+os.getenv('MONGO_PASSWORD')+"@"+os.getenv('MONGO_URL')+"/"+os.getenv('MONGO_DB')+"?"+os.getenv('MONGO_OPTIONS'))
            self._db=client[os.getenv('MONGO_DB')]
               
    
    def get_items(self):
        """
        Fetches all saved items from the session.

        Returns:
            list: The list of saved items.    
        """   
        
        # #Get Boards
        boards = self.get_board_details()     
            
        # #Get Board list
        board_lists=self.get_listinboard(boards["id"])
            

        active_board_list = next((board_list for board_list in board_lists if board_list['name'] == "Things To Do"), None)
        doing_board_list = next((board_list for board_list in board_lists if board_list['name'] == "Doing"), {"id":""})
        statuscomplete_list = next((board_list for board_list in board_lists if board_list['name'] == "Done"), {"id":""})
        if active_board_list==None:
            active_board_list = next((board_list for board_list in board_lists if board_list['name'] == "To Do"), {"id":""})

        #Get cards in the list
        card_lists=self.get_cardsinboard(boards["id"],active_board_list["id"],doing_board_list["id"],statuscomplete_list["id"])
    
        sorted_default_items=self.sort_items(card_lists)

        return sorted_default_items

    def get_board_details(self):
       
        db=self._db
        
        if(db['boards'].count_documents({}) == 0):
            boards_name = {"name": "todo items","date": datetime.utcnow()}
            boardscol = db["boards"]
            post_id = boardscol.insert_one(boards_name).inserted_id
            if(post_id==None):        
                raise CustomError('Error creating todo items board')
            else:
                return {
                "id": str(ObjectId(post_id)),
                "name": "todo items",
                }
        else:        
            document=db.boards.find_one({"name": "todo items"})
            return {
            "id": str(ObjectId(document['_id'])),
            "name": document["name"],
            }
                
            
    def get_listinboard(self,board_id):
        db=self._db

        board_lists = []   
            
        if(db['lists'].count_documents({}) == 0):
            list_name = [{'closed': False, 'idBoard': board_id, 'name': 'Things To Do', 'pos': 1}, {'closed': False, 'idBoard': board_id, 'name': 'Doing', 'pos': 2}, {'closed': False, 'idBoard': board_id, 'name': 'Done', 'pos': 3}]
            listscol = db["lists"]
            post_ids = listscol.insert_many(list_name).inserted_ids
            for json_item in list_name:
                board_lists.append({
                "id": str(ObjectId(json_item['_id'])),
                "name": json_item["name"],
                })
            return board_lists       
        else:         
            document=db.lists.find()
            for json_item in document:
                board_lists.append({
                "id": str(ObjectId(json_item['_id'])),
                "name": json_item["name"],
                })
            return board_lists   
    

    def get_cardsinboard(self,board_id,active_status_id,doing_status_id,complete_status_id):
        card_lists = []    
        card_dict = {}  

        db=self._db

        for json_item in db.cards.find({"idBoard": board_id}):        
            card_dict["id"] = str(ObjectId(json_item['_id']))
            card_dict["title"]  = json_item['name']
            card_dict["dateLastActivity"]  = str(json_item['dateLastActivity'])
            card_dict["active_list_id"]  = active_status_id
            card_dict["doing_list_id"]  = doing_status_id
            card_dict["complete_list_id"]  = complete_status_id

            if(active_status_id==json_item['idList']):
                card_dict["status"]  = 'Not Started'
            elif (doing_status_id==json_item['idList']):
                card_dict["status"]  = 'Doing'
            else:
                card_dict["status"]  = 'Done'
            card_lists.append(card_dict.copy())  

        return card_lists


    def get_item(self,id):
        """
        Fetches the saved item with the specified ID.

        Args:
            id: The ID of the item.

        Returns:
            item: The saved item, or None if no items match the specified ID.
        """
        items = self.get_items()
        return next((item for item in items if item['id'] == id), None)


    def add_item(self,title):
        """
        Adds a new item with the specified title to the session.

        Args:
            title: The title of the item.

        Returns:
            item: The saved item.
        """
        # #Get Boards
        boards = self.get_board_details()     
            
        # #Get Board list
        board_lists=self.get_listinboard(boards["id"])
            

        active_board_list = next((board_list for board_list in board_lists if board_list['name'] == "Things To Do"), None)
        if active_board_list==None:
            active_board_list = next((board_list for board_list in board_lists if board_list['name'] == "To Do"), None)
        #Create a new Card

        card = {"idBoard": boards["id"],
            "idList": active_board_list["id"],
            "name": title,
            "desc": "",
            "dateLastActivity": datetime.utcnow()}


        card_id = self._db.cards.insert_one(card).inserted_id
        
        if card_id==None:             
            raise CustomError('Error inserting card '+title)

        items = self.get_items()
    
        item = { 'id': str(ObjectId(card_id)), 'title': title, 'status': 'Not Started' }

        return item


    def save_item(self,item):
        """
        Updates an existing item in the database. If no existing item matches the ID of the specified item, An error is raised.
        
        Args:
            item: The item to update.
        """

        db=self._db

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
    
        existing_items = self.get_items()    
        updated_items = [item if item['id'] == existing_item['id'] else existing_item for existing_item in existing_items]    
    
        return item

    def remove_item(self,id):
        """
        removes an existing item in the session. If no existing item matches the ID of the specified item, nothing is saved.

        Args:
            item: The item id to remove.
        """

        db=self._db

        deleteitem =  {"_id": ObjectId(id)} 
        results=db.cards.delete_one(deleteitem)
    
        items = self.get_items()

        return id

    def sort_items(self,list_items):
        list_items= sorted(list_items,key=lambda item: (item['status'],item['title']))
        return list_items

    def create_trello_board(self):
        db=self._db

        board = {        
            "name": "To Services",
            "date": datetime.utcnow()}

        board_id = db.boards.insert_one(board).inserted_id
        
        if (board_id==None):          
            raise CustomError('Error finding creating board "To Service"')
        return str(ObjectId(board_id))


    def delete_trello_board(self,board_id):
        db=self._db

        deleteboard =  {"_id": ObjectId(board_id)} 
        results=db.boards.delete_one(deleteboard)   
        return (results.deleted_count>0)
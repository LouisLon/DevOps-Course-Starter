import pytest
import todo_app.app as app
from todo_app.data.session_items import ViewModel
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import requests_mock
import requests


@pytest.fixture
def trello_items():
    items=[{'dateLastActivity': '2020-10-01', 'id': '5f75c7b4f473030a20a30224', 'status': 'Doing', 'title': 'Staying at home'}, {'dateLastActivity': '2020-09-10', 'id': '5f58c9c6bf4667146a017e32', 'status': 'Done', 'title': 'Book my holiday'}, {'dateLastActivity': '2020-09-14', 'id': '5f5902cd7bdb1e12c8061d9a', 'status': 'Done', 'title': 'Fix Alicia book'}, {'dateLastActivity': '2020-09-14', 'id': '5f58c9c619f4fe1505e7290e', 'status': 'Not Started', 'title': 'Buy some clothes'}, {'dateLastActivity': '2020-09-10', 'id': '5f590331c1c56168a4cfe96b', 'status': 'Not Started', 'title': 'Fix Alicia book again'}, {'dateLastActivity': '2020-09-09', 'id': '5f58c9c64f6452685d239aaa', 'status': 'Not Started', 'title': 'Go for daily walks'}]
    return items

def test_viewmodel_items(trello_items):
    items = trello_items
    item_view_model = ViewModel(items) 
    assert item_view_model.items == items

def test_viewmodel_todoitems(trello_items):
    items = [todo_item for todo_item in trello_items if todo_item['status']=="Not Started"]     
    item_view_model = ViewModel(trello_items) 
    assert item_view_model.todoitems == items

def test_viewmodel_contains_todoitems(trello_items):       
    item_view_model = ViewModel(trello_items) 
    status_list = [ sub['status'] for sub in item_view_model.todoitems] 
    assert all(p == "Not Started" for p in status_list)

def test_viewmodel_doingitems(trello_items):
    items = [todo_item for todo_item in trello_items if todo_item['status']=="Doing"] 
    item_view_model = ViewModel(trello_items) 
    assert item_view_model.doingitems == items

def test_viewmodel_contains_doingitems(trello_items):       
    item_view_model = ViewModel(trello_items) 
    status_list = [ sub['status'] for sub in item_view_model.doingitems] 
    assert all(p == "Doing" for p in status_list)

def test_viewmodel_doneitems(trello_items):
    items = [todo_item for todo_item in trello_items if todo_item['status']=="Done"] 
    item_view_model = ViewModel(trello_items) 
    assert item_view_model.doneitems == items

def test_viewmodel_contains_doneitems(trello_items):       
    item_view_model = ViewModel(trello_items) 
    status_list = [ sub['status'] for sub in item_view_model.doneitems] 
    assert all(p == "Done" for p in status_list)

def test_viewmodel_contains_alldoneitems(trello_items):       
    item_view_model = ViewModel(trello_items) 
    status_list = [ sub['status'] for sub in item_view_model.show_all_done_items] 
    assert all(p == "Done" for p in status_list)

def test_viewmodel_contains_olddoneitems(trello_items):    
    todaydate=datetime.strptime(datetime.today().strftime('%d-%m-%Y'),'%d-%m-%Y')   
    item_view_model = ViewModel(trello_items)   
    date_list = [datetime.strptime((sub['dateLastActivity']).split(' ')[0],'%Y-%m-%d') for sub in item_view_model.older_done_items]     
    assert all(p <todaydate for p in date_list) and len(date_list)>0

def test_viewmodel_contains_recentdoneitems(trello_items):   
    todaydate=datetime.strptime(datetime.today().strftime('%d-%m-%Y'),'%d-%m-%Y')     
    item_view_model = ViewModel(trello_items) 
    date_list = [datetime.strptime((sub['dateLastActivity']).split(' ')[0],'%Y-%m-%d') for sub in item_view_model.recent_done_items]     
    assert all(p ==todaydate for p in date_list) #and len(date_list)>0


###Intergration testing

@pytest.fixture
def client():
    # Use our test integration config instead of the 'real' version
    file_path = find_dotenv('.env.test')
    load_dotenv(file_path, override=True)
    # Create the new app.
    test_app = app.create_app()
    
    # Use the app to create a test_client that can be used in our tests.
    with test_app.test_client() as client:        
        yield client
    
   
def test_index_page(client):     
    assert 'Book my holiday' in client.get('/').data.decode("utf-8") 

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
    

def test_index_page(requests_mock,client):    
    board_data='{"options":{"terms":[{"fields":["name"],"text":"todo items","phrase":true,"partial":false}],"modifiers":[],"modelTypes":["boards"],"partial":false},"boards":[{"id":"5f58c9c553d5e50e89e24311"}]}'
    listinboard_data='[{"id":"5f58c9c6b1674501de2aa921","name":"Things To Do","closed":false,"pos":1,"softLimit":null,"idBoard":"5f58c9c553d5e50e89e24311","subscribed":false},{"id":"5f58c9c65854784c5402cb5b","name":"Doing","closed":false,"pos":2,"softLimit":null,"idBoard":"5f58c9c553d5e50e89e24311","subscribed":false},{"id":"5f58c9c65cdab23790cb8014","name":"Done","closed":false,"pos":65538,"softLimit":null,"idBoard":"5f58c9c553d5e50e89e24311","subscribed":false}]'
    cardsinboard_data='[{"id":"5f58c9c619f4fe1505e7290e","checkItemStates":null,"closed":false,"dateLastActivity":"2020-09-14T12:08:29.289Z","desc":"We need to purchase winter clothes","descData":{"emoji":{}},"dueReminder":null,"idBoard":"5f58c9c553d5e50e89e24311","idList":"5f58c9c6b1674501de2aa921","idMembersVoted":[],"idShort":1,"idAttachmentCover":null,"idLabels":[],"manualCoverAttachment":false,"name":"Buy some clothes","pos":16384,"shortLink":"l13KNS0C","isTemplate":false,"badges":{"attachmentsByType":{"trello":{"board":0,"card":0}},"location":false,"votes":0,"viewingMemberVoted":false,"subscribed":false,"fogbugz":"","checkItems":2,"checkItemsChecked":0,"checkItemsEarliestDue":null,"comments":0,"attachments":0,"description":true,"due":null,"dueComplete":false,"start":null},"dueComplete":false,"due":null,"idChecklists":["5f58c9c760210f260b3a01b6"],"idMembers":[],"labels":[],"shortUrl":"https://trello.com/c/l13KNS0C","start":null,"subscribed":false,"url":"https://trello.com/c/l13KNS0C/1-buy-some-clothes","cover":{"idAttachment":null,"color":null,"idUploadedBackground":null,"size":"normal","brightness":"light"}},{"id":"5f58c9c64f6452685d239aaa","checkItemStates":null,"closed":false,"dateLastActivity":"2020-09-09T14:22:11.924Z","desc":"","descData":null,"dueReminder":null,"idBoard":"5f58c9c553d5e50e89e24311","idList":"5f58c9c6b1674501de2aa921","idMembersVoted":[],"idShort":2,"idAttachmentCover":null,"idLabels":[],"manualCoverAttachment":false,"name":"Go for daily walks","pos":49152,"shortLink":"qAi2nzpE","isTemplate":false,"badges":{"attachmentsByType":{"trello":{"board":0,"card":0}},"location":false,"votes":0,"viewingMemberVoted":false,"subscribed":false,"fogbugz":"","checkItems":0,"checkItemsChecked":0,"checkItemsEarliestDue":null,"comments":0,"attachments":0,"description":false,"due":null,"dueComplete":false,"start":null},"dueComplete":false,"due":null,"idChecklists":[],"idMembers":[],"labels":[],"shortUrl":"https://trello.com/c/qAi2nzpE","start":null,"subscribed":false,"url":"https://trello.com/c/qAi2nzpE/2-go-for-daily-walks","cover":{"idAttachment":null,"color":null,"idUploadedBackground":null,"size":"normal","brightness":"light"}},{"id":"5f590331c1c56168a4cfe96b","checkItemStates":null,"closed":false,"dateLastActivity":"2020-09-10T19:32:10.540Z","desc":"","descData":null,"dueReminder":null,"idBoard":"5f58c9c553d5e50e89e24311","idList":"5f58c9c6b1674501de2aa921","idMembersVoted":[],"idShort":5,"idAttachmentCover":null,"idLabels":[],"manualCoverAttachment":false,"name":"Fix Alicia book again","pos":81920,"shortLink":"Y7BrMK1w","isTemplate":false,"badges":{"attachmentsByType":{"trello":{"board":0,"card":0}},"location":false,"votes":0,"viewingMemberVoted":false,"subscribed":false,"fogbugz":"","checkItems":0,"checkItemsChecked":0,"checkItemsEarliestDue":null,"comments":0,"attachments":0,"description":false,"due":null,"dueComplete":false,"start":null},"dueComplete":false,"due":null,"idChecklists":[],"idMembers":[],"labels":[],"shortUrl":"https://trello.com/c/Y7BrMK1w","start":null,"subscribed":false,"url":"https://trello.com/c/Y7BrMK1w/5-fix-alicia-book-again","cover":{"idAttachment":null,"color":null,"idUploadedBackground":null,"size":"normal","brightness":"light"}},{"id":"5f75c7b4f473030a20a30224","checkItemStates":null,"closed":false,"dateLastActivity":"2020-10-01T12:12:36.841Z","desc":"","descData":null,"dueReminder":null,"idBoard":"5f58c9c553d5e50e89e24311","idList":"5f58c9c65854784c5402cb5b","idMembersVoted":[],"idShort":11,"idAttachmentCover":null,"idLabels":[],"manualCoverAttachment":false,"name":"Staying at home","pos":65535,"shortLink":"3gDOvH4B","isTemplate":false,"badges":{"attachmentsByType":{"trello":{"board":0,"card":0}},"location":false,"votes":0,"viewingMemberVoted":false,"subscribed":false,"fogbugz":"","checkItems":0,"checkItemsChecked":0,"checkItemsEarliestDue":null,"comments":0,"attachments":0,"description":false,"due":null,"dueComplete":false,"start":null},"dueComplete":false,"due":null,"idChecklists":[],"idMembers":[],"labels":[],"shortUrl":"https://trello.com/c/3gDOvH4B","start":null,"subscribed":false,"url":"https://trello.com/c/3gDOvH4B/11-staying-at-home","cover":{"idAttachment":null,"color":null,"idUploadedBackground":null,"size":"normal","brightness":"light"}},{"id":"5f58c9c6bf4667146a017e32","checkItemStates":null,"closed":false,"dateLastActivity":"2020-09-10T19:36:40.089Z","desc":"","descData":null,"dueReminder":null,"idBoard":"5f58c9c553d5e50e89e24311","idList":"5f58c9c65cdab23790cb8014","idMembersVoted":[],"idShort":3,"idAttachmentCover":null,"idLabels":[],"manualCoverAttachment":false,"name":"Book my holiday","pos":32768,"shortLink":"mXpbXxf9","isTemplate":false,"badges":{"attachmentsByType":{"trello":{"board":0,"card":0}},"location":false,"votes":0,"viewingMemberVoted":false,"subscribed":false,"fogbugz":"","checkItems":0,"checkItemsChecked":0,"checkItemsEarliestDue":null,"comments":0,"attachments":0,"description":false,"due":null,"dueComplete":false,"start":null},"dueComplete":false,"due":null,"idChecklists":[],"idMembers":[],"labels":[],"shortUrl":"https://trello.com/c/mXpbXxf9","start":null,"subscribed":false,"url":"https://trello.com/c/mXpbXxf9/3-book-my-holiday","cover":{"idAttachment":null,"color":null,"idUploadedBackground":null,"size":"normal","brightness":"light"}},{"id":"5f5902cd7bdb1e12c8061d9a","checkItemStates":null,"closed":false,"dateLastActivity":"2020-09-14T12:08:45.010Z","desc":"","descData":null,"dueReminder":null,"idBoard":"5f58c9c553d5e50e89e24311","idList":"5f58c9c65cdab23790cb8014","idMembersVoted":[],"idShort":4,"idAttachmentCover":null,"idLabels":[],"manualCoverAttachment":false,"name":"Fix Alicia book","pos":65536,"shortLink":"LdoweqNv","isTemplate":false,"badges":{"attachmentsByType":{"trello":{"board":0,"card":0}},"location":false,"votes":0,"viewingMemberVoted":false,"subscribed":false,"fogbugz":"","checkItems":0,"checkItemsChecked":0,"checkItemsEarliestDue":null,"comments":0,"attachments":0,"description":false,"due":null,"dueComplete":false,"start":null},"dueComplete":false,"due":null,"idChecklists":[],"idMembers":[],"labels":[],"shortUrl":"https://trello.com/c/LdoweqNv","start":null,"subscribed":false,"url":"https://trello.com/c/LdoweqNv/4-fix-alicia-book","cover":{"idAttachment":null,"color":null,"idUploadedBackground":null,"size":"normal","brightness":"light"}}]'
    requests_mock.get('https://api.trello.com/1/search', text=board_data)
    requests_mock.get('https://api.trello.com/1/boards/5f58c9c553d5e50e89e24311/lists', text=listinboard_data)
    requests_mock.get('https://api.trello.com/1/boards/5f58c9c553d5e50e89e24311/cards', text=cardsinboard_data)
    
    assert 'Book my holiday' in client.get('/').data.decode("utf-8") 

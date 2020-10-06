import pytest
import todo_app.app as app
import todo_app.data.session_items as session
from threading import Thread
import requests, os
from selenium import webdriver
from dotenv import load_dotenv, find_dotenv

@pytest.fixture(scope='module')
def test_app():
# Create the new board & update the board id environment variable
    board_id = session.create_trello_board()
    os.environ['TRELLO_BOARD_ID'] = board_id
    file_path = find_dotenv('.env')
    load_dotenv(file_path, override=True)
    # construct the new application
    application = app.create_app()
    # start the app in its own thread.
    thread = Thread(target=lambda: application.run(use_reloader=False))
    thread.daemon = True
    thread.start()
    yield app
    # Tear Down
    thread.join(1)
    session.delete_trello_board(board_id)

def test_board(test_app):
    assert os.environ['TRELLO_BOARD_ID']!=None

def test_split():
    s = 'hello world'
    assert s.split() == ['hello', 'world']
    # check that s.split fails when the separator is not    a string
    with pytest.raises(TypeError):
        s.split(2)



@pytest.fixture(scope="module")
def driver():
    with webdriver.Firefox() as driver:
        yield driver

def test_task_journey(driver, test_app):
    driver.get('http://localhost:5000/')
    assert driver.title == 'To-Do App'
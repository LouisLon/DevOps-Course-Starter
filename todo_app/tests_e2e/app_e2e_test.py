import pytest
import todo_app.app as app
import todo_app.data.session_items as session
from threading import Thread
import requests, os
from selenium import webdriver
from dotenv import load_dotenv, find_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

@pytest.fixture(scope='module')
def test_app():
# Create the new board & update the board id environment variable    
    file_path = find_dotenv('.env')
    load_dotenv(file_path, override=True)
    board_id = session.create_trello_board()
    os.environ['TRELLO_BOARD_ID'] = board_id
    # construct the new application
    application = app.create_app()
    # start the app in its own thread.
    thread = Thread(target=lambda: application.run(use_reloader=False))
    thread.daemon = True
    thread.start()
    yield app
    # Tear Down
    thread.join(1)
    #session.delete_trello_board(board_id)

# @pytest.fixture(scope="module")
# def driver():
#     with webdriver.Firefox() as driver:
#         yield driver

@pytest.fixture(scope='module')
def driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    with webdriver.Chrome('./chromedriver', options=opts) as driver:
        yield driver

def test_task_journey(driver, test_app):
    driver.get('http://localhost:5000/')    
    assert driver.title == 'To-Do App'

def test_add_item(driver,test_app):
    driver.get('http://localhost:5000/')    
    driver.find_element_by_name("title").send_keys("selenium created new item")
    driver.find_element_by_name("add_item").click()   
    driver.refresh()
    assert len(driver.find_elements(By.XPATH, '//li[contains(text(), "selenium created new item")]'))==1

def test_start_item(driver,test_app):
    driver.get('http://localhost:5000/')
  
    driver.find_element(By.XPATH, '//details').click()
    start_link=driver.find_element(By.XPATH, '//li[contains(text(), "selenium created new item")]/a[3]')
    start_link.click()
    driver.refresh()    
    driver.find_element(By.XPATH, '//summary[contains(text(),"Doing Items")]/..').click() 
    assert driver.find_elements(By.XPATH, '//li[contains(text(), "selenium created new item")]')[0].text=='selenium created new item - Doing Done'

def test_complete_item(driver,test_app):
    driver.get('http://localhost:5000/')

    driver.find_element(By.XPATH, '//summary[contains(text(),"Doing Items")]/..').click() 
    complete_link=driver.find_element(By.XPATH, '//li[contains(text(), "selenium created new item")]/a[2]')
    complete_link.click()
    driver.refresh()    
    assert driver.find_elements(By.XPATH, '//li[contains(text(), "selenium created new item")]')[0].text=='selenium created new item - Done To Do'

def test_incomplete_item(driver,test_app):
    driver.get('http://localhost:5000/')
    
    incomplete_link=driver.find_element(By.XPATH, '//li[contains(text(), "selenium created new item")]/a[2]')
    incomplete_link.click()
    driver.refresh()    
    driver.find_element(By.XPATH, '//summary[contains(text(),"ToDo Items")]/..').click() 
    assert driver.find_elements(By.XPATH, '//li[contains(text(), "selenium created new item")]')[0].text=='selenium created new item - Not Started DoneStart Item'


def test_delete_item(driver,test_app):
    driver.get('http://localhost:5000/')
    
    driver.find_element(By.XPATH, '//details').click()
    remove_link=driver.find_element(By.XPATH, '//li[contains(text(), "selenium created new item")]/a')
    remove_link.click()
    driver.refresh()
    assert len(driver.find_elements(By.XPATH, '//li[contains(text(), "selenium created new item")]'))==0
    session.delete_trello_board(os.environ['TRELLO_BOARD_ID'])
   
   

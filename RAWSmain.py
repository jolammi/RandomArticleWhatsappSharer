#!/usr/local/bin/python3
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import requests
import html2text


#Control variables---------------------------------------------------------------------------------------------

SELECTED_CONVERSATION = "INSERT_CONTACT_HERE" #ensure that this matches the contact or group name
PATH_TO_CHROMEDRIVER = 'C:\chromedriver_win32\chromedriver.exe'
PYTHON_PATH = r"C:\Users\INSERT_USERNAME_HERE\AppData\Local\Programs\Python\Python36\Memory\WebWhatsAppBot" #Used to save the WhatsApp login
SELECTED_LANGUAGE = "en" #this shows in wikipedia article and in the payload layout, currently "fi" or "en"
QR_CODE_PERIOD_SECONDS = 30 #seconds
SLEEP_BETWEEN_MESSAGES = 300 #seconds, 300 means once in five minutes

#/Control variables--------------------------------------------------------------------------------------------

def initialize_html2text():
    h = html2text.HTML2Text()
    h.ignore_links = True
    return h

def initialize_chromedriver(path,PYTHON_PATH):
    options = webdriver.ChromeOptions()
    options.add_argument(r"user-data-dir=" + PYTHON_PATH)
    driver = webdriver.Chrome(path, chrome_options=options)
    return driver

def print_help():
    """Remember to install the correct chromedriver version from
    http://chromedriver.chromium.org/downloads
    For the app to work, you need to give it access to your whatsapp web by scanning the
    QR code in the beginning. This only needs to be done on the first runng the apptime as the app saves your
    Whatsapp login. There is a 30-second period to scan the QR code, after which the app will start to look for the contact.
    - Set SELECTED_CONVERSATION to desired contact or group
    - Set PATH_TO_CHROMEDRIVER to the correct path"""
    return None


def get_random_article(SELECTED_LANGUAGE):
    page = requests.get('https://'+ SELECTED_LANGUAGE +'.wikipedia.org/wiki/Special:Random')
    page_text = page.text

    first_paragraph = str(page_text)
    first_paragraph = first_paragraph[first_paragraph.find("<p>") +3 :]
    first_paragraph = first_paragraph[: first_paragraph.find("</p>")]

    page_link = str(page_text)
    page_link = page_text[page_text.find("canonical"):]
    page_link = page_link[page_link.find("=")+2 : page_link.find("/>")-1]
    return first_paragraph, page_link


def parse_first_paragraph(text, handler,driver):
    text = handler.handle(text)
    symbols_to_replace = ["**", "_", "\\"]
    for i in symbols_to_replace:
        while text.find(i) != -1:
            text = text.replace(i,"")
    while text.find("\n") != -1:
            text = text.replace("\n"," ")
    while text.find("[") != -1:
        text = text[:text.find("[")] + text[text.find("[")+3:] #get rid of references like [1]
    return text

def open_whatsapp_web(QR_CODE_PERIOD_SECONDS,driver):
    driver.get('https://web.whatsapp.com')
    time.sleep(QR_CODE_PERIOD_SECONDS)
    return None

def send_whatsapp_message(conversation, driver, text, link, message_box):
    if SELECTED_LANGUAGE == "fi":
        message_box.send_keys("Tiesitkö, että:")
        ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(Keys.SHIFT).perform()
        message_box.send_keys(text)
        ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(Keys.SHIFT).perform()
        message_box.send_keys("Kiinnostuitko? Katso lisää: ")
        message_box.send_keys(link + "\n")
    else:
        message_box.send_keys("Did you know that:")
        ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(Keys.SHIFT).perform()
        message_box.send_keys(text)
        ActionChains(driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(Keys.SHIFT).perform()
        message_box.send_keys("Interested? Check: ")
        message_box.send_keys(link + "\n")
    return None

def open_conversation(conversation,driver):
    search_box = driver.find_element_by_xpath('//*[@title="Search or start new chat"]')
    search_box.click()
    search_box.send_keys(conversation + "\n")
    message_box = driver.find_element_by_css_selector('#main > footer > div._3pkkz.copyable-area > div._1Plpp > div')
    return message_box

def main_loop(SELECTED_LANGUAGE,SELECTED_CONVERSATION):
    print_help()
    driver = initialize_chromedriver(PATH_TO_CHROMEDRIVER,PYTHON_PATH)
    open_whatsapp_web(QR_CODE_PERIOD_SECONDS,driver)
    message_box = open_conversation(SELECTED_CONVERSATION,driver)
    handler = initialize_html2text()

    while True:
        try:
            text, link = get_random_article(SELECTED_LANGUAGE)
        except UnicodeEncodeError:
            print("Unicode error")
            continue
        text = parse_first_paragraph(text, handler,driver) 
        send_whatsapp_message(SELECTED_CONVERSATION,driver,text,link, message_box)
        time.sleep(SLEEP_BETWEEN_MESSAGES)
        # driver.quit()

main_loop(SELECTED_LANGUAGE, SELECTED_CONVERSATION)

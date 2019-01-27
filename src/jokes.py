from random import randint
from selenium import webdriver
from botwpp import *
from datetime import datetime
import time
from selenium.common.exceptions import NoSuchElementException

#Abertura do navegador
driver = webdriver.Chrome()
driver.get('https://web.whatsapp.com/')
input('Insira o QR e aperte enter')

while True:
    try:
        unread_chats = get_unread_chats(driver)
        for name in unread_chats:
            find_user(driver, name)
            time.sleep(3)
            messages = get_messages(driver)
            try:
                if(messages[-1][0][0] == '/'):
                    print('comando encontrado', messages[-1][0])
                    if(messages[-1][0] == '/piada'):
                        random_num = randint(0, jokes_tam-1)
                        message = jokes[random_num]
                        send_message(driver, message)
                        time.sleep(3)
                    else:
                        print('comando não encontrado')
            except:
                pass
    except NoSuchElementException: 
        pass
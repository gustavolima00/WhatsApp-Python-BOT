from selenium import webdriver
from botwpp import *
from datetime import datetime
import time
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome('chromedriver', service_args=["--verbose", "--log-path=/tmp/CHROMIUM_LOG"], options=chrome_options)
driver.get('https://web.whatsapp.com/')
input('Insira o QR e aperte enter')

contacts = {}

is_running = False
group_name = ''
players = {}
end_time = None

while True:
    if(is_running):
        time_now = datetime.now()
        if(time_now > end_time):
            find_user(driver, group_name)
            send_text(driver, 'time_over')
            is_running = False
            group_name = ''
            end_time = None
    try:
        chats = get_chats(driver)
        for chat in chats:
            if(chat.name != get_header(driver)):
                find_user(driver, chat.name)
                time.sleep(1)
            messages = get_messages(driver, chat.qnt_messages)
            print('Numero/Titulo do grupo:', chat.name)
            print('Tipo de conversa:', chat.chat_type)
            print('Número de mensagens não lidas:', chat.qnt_messages)
            print('Mensagens:', messages)
            # Comando para mensagens individuais
            if(chat.chat_type == 'normal'):
                for message in messages[chat.name]:
                    try:
                        run_command(driver, message)
                    except FileNotFoundError:
                        if(message.lower() == 'change_name'):
                            contacts[chat.name] = 'unamed'
                            send_text(driver, 'welcome')
                        else:
                            if(chat.name in contacts and contacts[chat.name] != 'unamed'):
                                send_text(driver, 'hello', contacts[chat.name])
                            elif(chat.name in contacts and contacts[chat.name] == 'unamed'):
                                contacts[chat.name] = message
                                send_text(driver, 'change_name', contacts[chat.name])
                            else:
                                contacts[chat.name] = 'unamed'
                                send_text(driver, 'welcome')
            # Comando para mensagens em grupo
            elif(chat.chat_type == 'group'):
                for user in messages:
                    for message in messages[user]:
                        try:
                            run_command(driver, message)
                        except FileNotFoundError:
                            if(message.lower() == 'start_game'):
                                if(user in contacts):
                                    time_now = datetime.now()
                                    end_time = time_now + timedelta(minutes=1)
                                    group_name = chat.name
                                    is_running = True
                                    send_text(driver, 'start_game', contacts[user])
                                else:
                                    send_text(driver, 'unknown_user', user)
                            else:
                                pass
            else:
                pass
        if('SLEEP' != get_header(driver)):    
            find_user(driver, 'SLEEP')
            time.sleep(3)
    except NoSuchElementException:
        pass

from selenium import webdriver
from botwpp import *
from werewolf import *
from datetime import datetime
import time
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome('chromedriver', service_args=["--verbose", "--log-path=/tmp/CHROMIUM_LOG"], options=chrome_options)
driver.get('https://web.whatsapp.com/')
contacts = get_contacts()

is_game_running = False
group_name = ''
players = {}
end_time = None

while True:
    if(is_game_running):
        time_now = datetime.now()
        if(time_now > end_time):
            find_user(driver, group_name)
            send_text(driver, 'time_over')
            is_game_running = False
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
                if(not chat.name in messages):
                    send_text(driver, 'bug_message')
                    continue
                for message in messages[chat.name][::-1]:
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
                                save_contacts(contacts)
                            else:
                                contacts[chat.name] = 'unamed'
                                send_text(driver, 'welcome')
            # Comando para mensagens em grupo
            elif(chat.chat_type == 'group'):
                for user in messages:
                    if(user == get_header(driver)):
                        send_text(driver, 'bug_message')
                        break
                    for message in messages[user][::-1]:
                        message = message.lower()
                        try:
                            run_command(driver, message)
                        except FileNotFoundError:
                            if(user in contacts):
                                if(is_game_running):
                                    if(message == 'join' and not user in players):
                                        players[user]=None
                                        send_text(driver, 'join', contacts[user])
                                    elif(message == 'players'):
                                        message = 'Jogadores:\n'
                                        for number in list(players):
                                            message += emoji.emojize(':bust_in_silhouette:'+ contacts[number]+'\n')
                                        send_message(driver, message)
                                    elif(message == 'force_start'):
                                        pass
                                else:
                                    if(message == 'start_game'):
                                        time_now = datetime.now()
                                        end_time = time_now + timedelta(minutes=1)
                                        group_name = chat.name
                                        is_game_running = True
                                        players[user]=None
                                        send_text(driver, 'start_game', contacts[user])
                            else:
                                send_text(driver, 'unknown_user', user)

            if('SLEEP' != get_header(driver)):    
                find_user(driver, 'SLEEP')
                time.sleep(3)
    except NoSuchElementException:
        pass

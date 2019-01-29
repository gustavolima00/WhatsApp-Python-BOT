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
print('contacts', contacts)

is_game_running = False
is_game_preparing = False
group_name = ''
players = {}
end_time = None

while True:
    if(is_game_preparing):
        time_now = datetime.now()
        if(time_now > end_time):
            find_user(driver, group_name)
            end_time = None
            if(start_game(driver, group_name, players)):
                end_time = None
                is_game_preparing = False
                is_game_running = True
            else:
                send_text(driver, 'start_error')
                end_time = None
                is_game_running = False
                is_game_preparing = False
                group_name = ''
            find_user(driver, group_name)
            show_players(driver, players, contacts)
            
    try:
        unread_chats = get_unread_chats(driver)
        for contact_name in unread_chats:
            messages = get_messages(driver, contact_name)
            title = get_header(driver)
            print('Conversation:', title)
            print('Messages:', messages)
            #Se o título da conversa começa com + é uma pessoa
            if(title[0] == '+'): 
                if(not title in messages):
                    send_text(driver, 'bug_message')
                    continue
                for message in messages[title][::-1]:
                    try:
                        run_command(driver, message)
                    except FileNotFoundError:
                        if(message.lower() == 'change_name'):
                            contacts[title] = 'unamed'
                            send_text(driver, 'welcome')
                        else:
                            if(title in contacts and contacts[title] != 'unamed'):
                                send_text(driver, 'hello', contacts[title])
                            elif(title in contacts and contacts[title] == 'unamed'):
                                contacts[title] = message
                                send_text(driver, 'change_name', contacts[title])
                                save_contacts(contacts)
                            else:
                                contacts[title] = 'unamed'
                                send_text(driver, 'welcome')
            # Comando para mensagens em grupo
            else:
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
                                if(is_game_preparing or is_game_running):
                                    if(message == 'players'):
                                        show_players(driver, players, contacts)

                                elif(is_game_preparing and not is_game_running):
                                    if(message == 'join' and not user in players):
                                        players[user]=None
                                        send_text(driver, 'join', contacts[user])
                                    elif(message == 'force_start'):
                                        if( start_game(driver, group_name, players)):
                                            find_user(driver, group_name)
                                            show_players(driver, players, contacts)
                                            end_time = None
                                            is_game_preparing = False
                                            is_game_running = True
                                        else:
                                            find_user(driver, group_name)
                                            send_text(driver, 'start_error')
                                            group_name = ''
                                            end_time = None
                                            is_game_preparing = False
                                            is_game_running = False
                                elif(not is_game_preparing and is_game_running):
                                    pass
                                else:
                                    if(message == 'start_game'):
                                        time_now = datetime.now()
                                        end_time = time_now + timedelta(minutes=1)
                                        group_name = title
                                        is_game_preparing = True
                                        players[user]=None
                                        send_text(driver, 'start_game', contacts[user])
                            else:
                                send_text(driver, 'unknown_user', user)

            if('SLEEP' != get_header(driver)):    
                find_user(driver, 'SLEEP')
                time.sleep(3)
    except NoSuchElementException:
        find_user(driver, 'SLEEP')
        time.sleep(3)

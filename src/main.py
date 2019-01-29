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

players = []
game = Game(players)

while True:
    game.game_check(driver)
            
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
                    run_command(driver, message, title)
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
                        run_command(driver, message, user)
                        if(user in contacts):
                            if(message == 'players'):
                                game.show_players(driver)

                            elif(message == 'join'):
                                player = Player(user, contacts[user])
                                game.add_player(driver, player)
            
                            elif(message == 'force_start'):
                                game.start_game(driver)

                            elif(message == 'start_game'):
                                player = Player(user, contacts[user])
                                game.prepare_game(driver, title, player)
                            elif(message == 'flee'):
                                player = Player(user, contacts[user])
                                game.remove_player(driver, player)

                        else:
                            send_text(driver, 'unknown_user', user)

            if('SLEEP' != get_header(driver)):    
                find_user(driver, 'SLEEP')
                time.sleep(3)
    except NoSuchElementException:
        find_user(driver, 'SLEEP')
        time.sleep(3)

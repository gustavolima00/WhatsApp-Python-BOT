from selenium import webdriver
from botwpp_test import *
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

input('Insira o QR code e aperte enter')
find_user(driver, 'SLEEP')
time.sleep(1)

while True:
    if('SLEEP' != get_header(driver)):    
        find_user(driver, 'SLEEP')
        time.sleep(1)
    game.game_check(driver)         
    try:
        unread_chats = get_unread_chats(driver)
        for contact_name in unread_chats:
            messages = get_messages(driver, contact_name)
            title = contact_name
            print('Conversation:', title)
            print('Messages:', messages)
            #Se o título da conversa começa com + é uma pessoa
            if(title[0] == '+'): 
                if(not title in messages):
                    send_text(driver, title, 'bug_message')
                    continue
                for message in messages[title][::-1]:
                    run_command(driver, message, title)
                    if(title in game.has_action):
                        for player in game.players:
                            if(player.phone == title):
                                game.run_action(driver, player, message)
                                break
                    if(message.lower() == 'name'):
                        contacts[title] = 'unamed'
                        send_text(driver, title, 'change_name')
                    else:
                        if(title in contacts and contacts[title] != 'unamed'):
                            if('oi' in message.lower()):
                                send_text(driver, title, 'hello', contacts[title])
                        elif(title in contacts and contacts[title] == 'unamed'):
                            contacts[title] = message
                            send_text(driver, title, 'new_name', contacts[title])
                            save_contacts(contacts)
                        else:
                            contacts[title] = 'unamed'
                            send_text(driver, title, 'welcome')
                            send_text(driver, title, 'change_name')
            # Comando para mensagens em grupo
            else:
                for user in messages:
                    if(user == get_header(driver)):
                        send_text(driver, title, 'bug_message')
                        continue
                    for message in messages[user][::-1]:
                        message = message.lower()
                        run_command(driver, message, user)
                        if(user in contacts):
                            if(message == 'jogadores'):
                                game.show_players(driver)

                            elif(message == 'entrar'):
                                player = Player(user, contacts[user])
                                game.add_player(driver, player)
            
                            elif(message == 'force'):
                                game.start_game(driver)

                            elif(message == 'iniciar'):
                                player = Player(user, contacts[user])
                                game.prepare_game(driver, title, player)
                            elif(message == 'sair'):
                                player = Player(user, contacts[user])
                                game.remove_player(driver, player)
                            elif(message == 'end'):
                                game.end_game(driver)
                            elif(message == 'tempo'):
                                game.show_time(driver)
                            elif(message == 'extend'):
                                game.extend(driver)
                            elif(message == 'skip'):
                                game.skip()

                        else:
                            send_text(driver, title, 'unknown_user', user)
    except NoSuchElementException:
        pass
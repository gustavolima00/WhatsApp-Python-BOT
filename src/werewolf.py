from botwpp import *
import random
import emoji

def save_contacts(contacts):
    file = open('contacts.txt','w') 
    for number in contacts:
        file.write(number) 
        file.write('#') 
        file.write(contacts[number])
        file.write('\n') 
    
    file.close()

def get_contacts():
    contacts = {}
    try:
        file = open('contacts.txt','r')
        lines = file.read().split('\n')
        for line in lines:
            content = line.split('#')
            if(len(content)==2):
                contacts[content[0]]=content[1]
            else:
                pass
    except FileNotFoundError:
        pass
    return contacts

def start_game(driver, group_name, players):
    try:
        arq = open('game_messages/game_start.txt', 'r')
        text = arq.read()
        arq.close()
        find_user(driver, group_name)
        send_message(driver, text)
        vg_roles = ['cursed', 'detective', 'drunk']
        random.shuffle(vg_roles)
        ww_roles = []
        random.shuffle(ww_roles)
        for player in players:
            role = vg_roles.pop()
            arq_path = 'roles_messages/' + role + '.txt'
            arq = open(arq_path, 'r')
            text = arq.read()
            arq.close()
            players[player]=role
            find_user(driver, player)
            send_message(driver, text)
        return True
    except:
        return False
    

def show_players(driver, players, contacts):
    message = '*Jogadores*:\n'
    for number in list(players):
        if(players[number] == None):
            message += emoji.emojize(':bust_in_silhouette:')
        elif(players[number] == 'dead'):
            message += emoji.emojize(':skull:')
        else:
            message += emoji.emojize(':slightly_smiling_face:')    
        message += contacts[number]+'\n'
    send_message(driver, message)

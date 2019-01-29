from botwpp import *
import random
import emoji
from datetime import datetime, timedelta

ALIVE = 1
DEAD = 2

class Player:
    def __init__(self, number, name):
        self.number = number
        self.name = name
        self.status = 0 #dead or alive
        self.role = None
        self.especial_power = 0
        self.actions = 0

    def set_role(self, role):
        self.role = role
        self.status = ALIVE
        #roles com poderes especiais
        if(role == ''):
            especial_power = 1
    
    def kill(self):
        self.status = DEAD
        self.role = None
        self.especial_power = 0
        self.actions = 0

OFF = 0
PREPARING = 1
RUNNING = 2

NIGHT = 1
DAY = 2
VOTING = 3

class Game:
    def __init__(self, players):
        self.players = players
        self.status = OFF
        self.group_name = ''
        self.time_now = datetime.now()
        self.next_time = None
        self.game_time = None

    def prepare_game(self, driver, group_name, player):
        if(self.status != OFF):
            return
        self.status = PREPARING
        self.next_time = self.time_now + timedelta(minutes=5)
        self.group_name = group_name
        send_text(driver, group_name, 'start_game', player.name)
        self.players.append(player)

    #Toma as decisões no jogo
    def game_check(self, driver):
        if(self.status == OFF):
            return
        self.time_now = datetime.now()
        if(self.status == PREPARING and self.time_now > self.next_time):
            self.start_game(driver)       
            return
        if(self.status == RUNNING and self.time_now > self.next_time):
            self.end_game(driver)
            return

    def start_game(self, driver):
        if(self.status != PREPARING):
            return
        arq = open('game_messages/game_start.txt', 'r')
        text = arq.read()
        arq.close()
        send_message(driver, self.group_name, text)

        vg_roles = ['cursed', 'detective', 'drunk']
        random.shuffle(vg_roles)
        ww_roles = []
        random.shuffle(ww_roles)

        for player in self.players:
            role = vg_roles.pop()
            arq_path = 'roles_messages/' + role + '.txt'
            arq = open(arq_path, 'r')
            text = arq.read()
            arq.close()
            player.set_role(role)
            send_message(driver, player.number, text)

        self.status = RUNNING
        self.game_time = NIGHT
        self.next_time = self.time_now + timedelta(seconds=90)
        self.show_players(driver)

    def end_game(self, driver):
        self.status = OFF
        self.group_name = ''
        self.time_now = datetime.now()
        self.next_time = None
        self.game_time = None
        self.players.clear()
        send_message(driver, self.group_name, 'O jogo foi finalizado')

    def show_players(self, driver):
        if(self.status == OFF):
            return
        message = '*Jogadores*:\n'
        if(self.status == PREPARING):
            for player in self.players:
                message += emoji.emojize(':bust_in_silhouette:')  
                message += player.name+'\n'

        if(self.status == RUNNING):
            for player in self.players:

                if(player.status == DEAD):
                    message += emoji.emojize(':skull:')
                elif(player.status == ALIVE):
                    message += emoji.emojize(':slightly_smiling_face:') 

                message += player.name+'\n'
        send_message(driver, self.group_name, message)

    def add_player(self, driver, new_player):
        if(self.status != PREPARING):
            return
        for player in self.players:
            if(player.number == new_player.number):
                return
        self.players.append(new_player)
        send_text(driver, self.group_name, 'join', new_player.name)
    
    def remove_player(self, driver, r_player):
        if(self.status != PREPARING and self.status != RUNNING):
            return
        
        for player in self.players:
            if(player.number == r_player.number):
                send_text(driver, self.group_name, 'flee', player.name)
                self.players.remove(player)
                return
    def run_nigth(self, driver):
        for player in self.players:
            if(player.role == 'wolf'):
                pass
                



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
    

def run_command(driver, command, user):
    try:
        arq_path = 'commands/' + command.lower() + '.txt'
        arq = open(arq_path, 'r')
        text = arq.read()
        phrases = text.split('#')
        num = len(phrases)
        arq.close()
        random_num = randint(0, num-1)
        message = phrases[random_num]
        send_message(driver, user, message)
    except FileNotFoundError:
        pass

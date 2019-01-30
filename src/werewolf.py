from botwpp import *
import random
import emoji
from datetime import datetime, timedelta

# Player status
ALIVE = 1
DEAD = 2
# Role tipes
WW = 1
VG = 2
SK = 3
# Game status
OFF = 0
PREPARING = 1
RUNNING = 2
# Game stages
NIGHT = 1
DAY = 2
VOTING = 3

QNT_MIN = 2
# Roles
VG_ROLES = ['villager']
NUM_VG_ROLES = len(VG_ROLES)
WW_ROLES = ['wolf']
NUM_WW_ROLES = len(WW_ROLES)

class Player:
    def __init__(self, number, name):
        self.number = number
        self.name = name
        self.status = 0 #dead or alive
        self.role = None
        self.role_type = None
        self.especial_power = 0
        self.actions = 0
        self.status = None

    def set_role(self, role):
        self.role = role
        if(role in VG_ROLES):
            self.role_type = VG
        elif(role in WW_ROLES):
            self.role_type = WW
        else:
            pass
        self.status = ALIVE
        #roles com poderes especiais
        if(role == ''):
            especial_power = 1
    
    def kill(self):
        self.status = DEAD
        self.role = None
        self.especial_power = 0
        self.actions = 0

class Game:
    def __init__(self, players):
        self.players = players
        self.num_players = len(self.players)
        self.num_ww = 0
        self.num_vg = 0
        self.status = OFF
        self.group_name = ''
        self.time_now = datetime.now() 
        self.next_time = self.time_now- timedelta(minutes=5)
        self.game_time = 0
        self.options = {}
        self.actions = {}

    def prepare_game(self, driver, group_name, player):
        if(self.status != OFF):
            return
        self.status = PREPARING
        self.time_now = datetime.now()
        self.next_time = self.time_now + timedelta(minutes=5)
        self.group_name = group_name
        send_text(driver, group_name, 'start_game', player.name)
        self.players.append(player)

    #Toma as decisões no jogo
    def game_check(self, driver):
        if(self.status == OFF):
            return
        self.time_now = datetime.now()
        time_remaning = (self.next_time - self.time_now).seconds
        if(self.status == PREPARING):
            if(self.time_now>self.next_time):
                self.start_game(driver)
            elif(time_remaning == 60):
                send_text(driver, self.group_name, 'time_remaning', '1', '0')
            elif(time_remaning == 180):
                send_text(driver, self.group_name, 'time_remaning', '3', '0')
            elif(time_remaning == 30):
                send_text(driver, self.group_name, 'time_remaning', '0', '30')
            elif(time_remaning == 10):
                send_text(driver, self.group_name, 'time_remaning', '0', '10')
                      
            return
        if(self.status == RUNNING):
            if(self.game_time == NIGHT):
                if(self.time_now>self.next_time):
                    self.run_day(driver)
                elif(len(self.options)==0):
                    self.run_day(driver)
            elif(self.game_time == DAY):
                if(self.time_now>self.next_time):
                    self.run_votation(driver)
            elif(self.game_time == VOTING):
                if(self.time_now>self.next_time):
                    self.run_lynch(driver)
                    self.run_nigth(driver)
                elif(len(self.options)==0):
                    self.run_lynch(driver)
                    self.run_nigth(driver)
            return

    def show_time(self, driver):
        time_remaning = (self.next_time - self.time_now).seconds
        minutes = str(int(time_remaning/60))
        seconds = str(time_remaning%60)
        send_text(driver, self.group_name, 'time_remaning', minutes, seconds)

    def extend(self, driver):
        if(self.status == PREPARING):
            self.time_now = datetime.now()
            self.next_time = self.time_now + timedelta(minutes=5)
            send_text(driver, self.group_name, 'time_remaning', '5', '0')

    def start_game(self, driver):
        random.shuffle(self.players)
        num_players = len(self.players)
        self.num_vg = 0
        self.num_ww = 0
        if(self.status != PREPARING):
            return
        if(num_players<QNT_MIN or num_players<2):
            send_text(driver, self.group_name, 'not_enough_players')
            self.end_game(driver)
            return
        send_text(driver, self.group_name, 'game_start')
        
        i=0
        for player in self.players:
            #Primeiro jogador sempre é um vilager
            if(i==0):
                role_num = randint(0, NUM_VG_ROLES-1)
                role = VG_ROLES[role_num]
                self.num_vg+=1
            #Segundo jogador sempre é um lobo
            elif(i==1):
                role_num = randint(0, NUM_WW_ROLES-1)
                role = WW_ROLES[role_num]
                self.num_ww+=1
            #Os demais jogadores são aleatórios
            else:
                #Máximo de 30% de lobos o próximo player será da vila
                if(self.num_players*0.3-self.num_ww < 1):
                    num = VG
                else:
                    num = randint(WW,VG)
                if(num == VG):
                    role_num = randint(0, NUM_VG_ROLES-1)
                    role = VG_ROLES[role_num]
                    self.num_vg+=1
                elif(num == WW):
                    role_num = randint(0, NUM_WW_ROLES-1)
                    role = WW_ROLES[role_num]
                    self.num_ww+=1
                else:
                    role = ''           
            arq_path = 'roles_messages/' + role + '.txt'
            arq = open(arq_path, 'r')
            text = arq.read()
            arq.close()
            player.set_role(role)
            send_message(driver, player.number, text)
            i+=1

        self.status = RUNNING
        self.game_time = NIGHT
        self.run_nigth(driver)

    def end_game(self, driver):
        send_message(driver, self.group_name, 'O jogo foi finalizado')
        self.num_players = 0
        self.num_ww = 0
        self.num_vg = 0
        self.status = OFF
        self.group_name = ''
        self.game_time = 0
        self.options.clear()
        self.actions.clear()
        self.players.clear()

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
        self.num_players = len(self.players)
    
    def run_action(self, driver, player, choice):
        try:
            choice = int(choice)-1
        except:
            return
        options = self.options.get(player.number)
        chosen_player = options[choice]
        if(chosen_player == None):
            return
        
        send_message(driver, player.number, 'Opção aceita')
        send_text(driver, player.number, 'option_accepted', chosen_player.name)
        self.actions[player]=chosen_player
        del self.options[player.number]
        if(self.game_time == VOTING):
            send_text(driver, self.group_name, 'player_voted_lynch', player.name, chosen_player.name)

    def remove_player(self, driver, r_player):
        if(self.status != PREPARING and self.status != RUNNING):
            return
        
        for player in self.players:
            if(player.number == r_player.number):
                send_text(driver, self.group_name, 'flee', player.name)
                self.players.remove(player)
                self.num_players = len(self.players)
                return
    
    def skip(self):
        self.time_now = datetime.now() 
        self.next_time = self.time_now- timedelta(minutes=5)
    def run_nigth(self, driver):
        self.options.clear()
        self.next_time = self.time_now + timedelta(seconds=90)
        for player in self.players:
            if(player.status == ALIVE):
                if(player.role_type == WW):
                    self.options[player.number]=[]
                    for other_player in self.players:
                        if(other_player.status == ALIVE):
                            if(other_player !=  player):
                                self.options[player.number].append(other_player)                    
                    send_action(driver, 'kill', player.number, self.options[player.number])
                elif(player.role_type == VG):
                    pass
                else:
                    pass
        send_text(driver, self.group_name, 'night')
        self.show_players(driver)

    def run_day(self, driver):
        self.options.clear()
        self.next_time = self.time_now + timedelta(seconds=90)
        ww_kill=[]
        for player in self.actions:
            chosen_player = self.actions[player]
            if(player.role == 'wolf'):
                ww_kill.append(chosen_player)
        if(len(ww_kill)==0):
            send_text(driver, self.group_name, 'no_attack')
        else:
            for player in ww_kill:
                send_text(driver, player.number, 'wolves_eat_you')
                if(False):
                    pass
                else:
                    send_text(driver, self.group_name, 'default_eaten', player.name)
                player.kill()
        self.game_time = DAY
        send_text(driver, self.group_name, 'day')
        self.show_players(driver)
   
    def run_votation(self, driver):
        self.options.clear()
        self.next_time = self.time_now + timedelta(seconds=90)
        self.game_time = VOTING
        send_text(driver, self.group_name, 'votation')
        for player in self.players:
            if(player.status == ALIVE):
                self.options[player.number]=[]
                for other_player in self.players:
                    if(other_player.status == ALIVE):
                        if(other_player != player):
                            self.options[player.number].append(other_player)                    
                send_action(driver, 'vote', player.number, self.options[player.number])

    def run_lynch(self, driver):
        self.options.clear()
        lynch_players = {}
        max_votes = 0
        draw = True
        
        lynch_player = None
        for player in self.players:
            if(player.status == ALIVE):
                lynch_players[player]=0

        for player in self.actions:
            chosen_player = self.actions[player]
            lynch_players[chosen_player]+=1
            if(lynch_players[chosen_player] > max_votes):
                max_votes = lynch_players[chosen_player]
                lynch_player = chosen_player
                draw = False
            elif(lynch_players[chosen_player] == max_votes):
                draw = True

        if(max_votes == 0):
            send_text(driver, self.group_name, 'no_lynch_votes')
        elif(draw):
            send_text(driver, self.group_name, 'lynch_tie')
        else:
            send_text(driver, self.group_name, 'lynch_kill', lynch_player.name)
            lynch_player.kill()

        
    def is_alive(player):
        return player.status==ALIVE

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
    message = ''
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
        return

def send_action(driver, action, user, other_players):
    message = ''
    try:
        arq_path = 'actions/' + action.lower() + '.txt'
        arq = open(arq_path, 'r')
        text = arq.read()
        phrases = text.split('#')
        num = len(phrases)
        arq.close()
        random_num = randint(0, num-1)
        message += phrases[random_num]
    except FileNotFoundError:
        print('Erro em send_action')
        return
    i=1
    for player in other_players:
        line = '*'+str(i)+'*. '+player.name+'\n'
        message+=line
        i+=1
    send_message(driver, user, message)

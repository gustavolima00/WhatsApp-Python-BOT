from  botwpp import get_header
from  botwpp import send_message
from  botwpp import send_text
from  botwpp import get_unread_chats
from  botwpp import get_messages
import random
from random import randint
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
LYNCH = 3
QNT_MIN = 2
# Roles
VG_ROLES = ['villager']
NUM_VG_ROLES = len(VG_ROLES)
WW_ROLES = ['wolf']
NUM_WW_ROLES = len(WW_ROLES)

class Player:
    def __init__(self, phone, name):
        self.phone = phone
        self.name = name
        self.status = 0 #dead or alive
        self.role = None
        self.role_type = None
        self.especial_power = 0
        self.status = None
        self.will_have_attack = True
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
    # Mata jogador e retorna tipo de role que jogador era
    def kill(self):
        self.status = DEAD
        return self.role_type
    def get_role(self):
        if(self.role == 'villager'):
            return emoji.emojize('Aldeão :blond-haired_person:')
        elif(self.role == 'wolf'):
            return emoji.emojize('Lobisomem :wolf_face:')
        elif(self.role == 'drunk'):
            return emoji.emojize('Bebum :clinking_beer_mugs:')    
        else:
            return ''
            
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
        self.game_time = 0 #Day, night ou lynch 
        self.has_action = {}
        self.actions = {}
        self.can_attack = True
        self.can_lynch = True
        self.voted_players = {}
        self.clear_votes()
    # Inicia o jogo e adiciona player que iniciou 
    def prepare_game(self, driver, group_name, player):
        if(self.status != OFF):
            return
        self.status = PREPARING
        self.time_now = datetime.now()
        self.next_time = self.time_now + timedelta(minutes=5)
        self.group_name = group_name
        send_text(driver, group_name, 'start_game', player.name)
        self.players.append(player)
    # Checa as açoes e players para finalizar ou avançar
    def game_check(self, driver):
        if(self.status == OFF):
            return
        self.time_now = datetime.now()
        time_remaning = (self.next_time - self.time_now).seconds
        # Açoes para jogo em preparação
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
        # Ações para jogo rolando
        if(self.status == RUNNING):
            #Condiçoes de vitória
            if(self.num_ww == 0):
                send_text(driver, self.group_name, 'village_wins')
                self.show_roles(driver)
                self.end_game(driver)
            elif(self.num_vg<=self.num_ww):
                send_text(driver, self.group_name, 'wolves_win')
                self.show_roles(driver)
                self.end_game(driver)
            #Dia
            if(self.game_time == NIGHT):
                if(self.time_now>self.next_time):
                    self.wolves_eat(driver)
                    self.run_day(driver)
                elif(len(self.has_action)==0):
                    self.wolves_eat(driver)
                    self.run_day(driver)
            #Linchamento
            elif(self.game_time == DAY):
                if(self.time_now>self.next_time):
                    self.start_lynch(driver)
            #Noite
            elif(self.game_time == LYNCH):
                if(self.time_now>self.next_time):
                    self.lynch(driver)
                    self.run_nigth(driver)
                elif(len(self.has_action)==0):
                    self.lynch(driver)
                    self.run_nigth(driver)
            return
    def start_game(self, driver):
        #Roles especias que só tem uma por jogo
        vg_especial = ['drunk']
        random.shuffle(vg_especial)
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
                if(len(vg_especial) > 0):
                    role = vg_especial.pop()
                else:
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
                    if(len(vg_especial) > 0):
                        role = vg_especial.pop()
                    else:
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
            send_message(driver, player.phone, text)
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
        self.has_action.clear()
        self.actions.clear()
        self.players.clear()
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
    def show_roles(self, driver):
        message = 'Jogadores restantes e papeis:\n'
        for player in self.players:
            if(player.status == ALIVE):
                message += '*' + player.name + '*: ' + player.get_role() + '\n'
        send_message(driver, self.group_name, message)
    def add_player(self, driver, new_player):
        if(self.status != PREPARING):
            return
        for player in self.players:
            if(player.phone == new_player.phone):
                return
        self.players.append(new_player)
        send_text(driver, self.group_name, 'join', new_player.name)
        self.num_players = len(self.players)  
    def run_action(self, driver, player, choice):
        try:
            choice = int(choice)-1
        except:
            return
        options = self.has_action.get(player.phone)
        chosen_player = options[choice]
        if(chosen_player == None):
            return    
        send_message(driver, player.phone, 'Opção aceita')
        send_text(driver, player.phone, 'option_accepted', chosen_player.name)
        # Ações do dia
        if(self.game_time == DAY):
            pass
        # Açoes da noite
        elif(self.game_time == NIGHT):
            if(player.role_type == WW):
                self.voted_players[chosen_player]+=1
                for player in self.players:
                    if(player.role_type == WW and player.status == ALIVE and player != chosen_player):
                        send_text(driver, player.phone, 'player_voted_kill', player.name, chosen_player.name)
        # Linchamento 
        elif(self.game_time == LYNCH):
            self.voted_players[chosen_player]+=1
            send_text(driver, self.group_name, 'player_voted_lynch', player.name, chosen_player.name)
    def remove_player(self, driver, r_player):
        if(self.status != PREPARING and self.status != RUNNING):
            return
        
        for player in self.players:
            if(player.phone == r_player.phone):
                send_text(driver, self.group_name, 'flee', player.name)
                self.players.remove(player)
                self.num_players = len(self.players)
                return
    def skip(self):
        self.time_now = datetime.now() 
        self.next_time = self.time_now- timedelta(minutes=5)
    def run_nigth(self, driver):
        self.next_time = self.time_now + timedelta(seconds=90)
        self.game_time = NIGHT
        self.send_actions(driver)
        send_text(driver, self.group_name, 'night')
    def run_day(self, driver):
        self.next_time = self.time_now + timedelta(seconds=90)
        self.game_time = DAY
        self.send_actions(driver)
        send_text(driver, self.group_name, 'day')
        self.show_players(driver)
    def start_lynch(self, driver):
        self.next_time = self.time_now + timedelta(seconds=90)
        self.game_time = LYNCH
        self.send_actions(driver)
        send_text(driver, self.group_name, 'votation')   
    def wolves_eat(self, driver):
        self.has_action.clear()
        max_votes = 0
        draw = True
        eaten_player = None
        for chosen_player in self.voted_players:
            if(self.voted_players[chosen_player] > max_votes):
                max_votes = self.voted_players[chosen_player]
                eaten_player = chosen_player
                draw = False
            elif(self.voted_players[chosen_player] == max_votes):
                draw = True
                
        if(max_votes == 0):
            send_text(driver, self.group_name, 'no_attack')
        else:
            send_text(driver, eaten_player.phone, 'wolves_eat_you')
            if(eaten_player.role == 'drunk'):
                send_text(driver, self.group_name, 'drunk_eaten', eaten_player.name)
                self.can_attack = False
            else:
                send_text(driver, self.group_name, 'default_eaten', eaten_player.name)
            self.kill(eaten_player)
        self.clear_votes()
    def lynch(self, driver):
        self.has_action.clear()
        max_votes = 0
        draw = True
        lynch_player = None
        for chosen_player in self.voted_players:
            if(self.voted_players[chosen_player] > max_votes):
                max_votes = self.voted_players[chosen_player]
                lynch_player = chosen_player
                draw = False
            elif(self.voted_players[chosen_player] == max_votes):
                draw = True
        if(max_votes == 0):
            send_text(driver, self.group_name, 'no_lynch_votes')
        elif(draw):
            send_text(driver, self.group_name, 'lynch_tie')
        else:
            if(False):
                pass
            else:
                send_text(driver, self.group_name, 'lynch_kill', lynch_player.name, lynch_player.name, lynch_player.get_role())
                self.kill(lynch_player)
        self.clear_votes() 
    def send_actions(self, driver):
        # Ações do dia
        if(self.game_time == DAY):
            pass
        # Ações da noite
        elif(self.game_time == NIGHT):
            for player in self.players:
                if(player.status == ALIVE):
                    if(player.role_type == WW and self.can_attack):
                        self.has_action[player.phone]=[]
                        for other_player in self.players:
                            if(other_player.status == ALIVE and other_player.role_type != WW):
                                if(other_player !=  player):
                                    self.has_action[player.phone].append(other_player)                    
                        send_action(driver, 'kill', player.phone, self.has_action[player.phone])
                    elif(player.role_type == VG):
                        pass
                    else:
                        pass
            if(not self.can_attack):
                self.can_attack = True
        # Votação para linchamento 
        elif(self.game_time == LYNCH):
            if(self.can_lynch):
                for player in self.players:
                    if(player.status == ALIVE):
                        self.has_action[player.phone]=[]
                        for other_player in self.players:
                            if(other_player.status == ALIVE):
                                if(other_player != player):
                                    self.has_action[player.phone].append(other_player)                    
                        send_action(driver, 'vote', player.phone, self.has_action[player.phone])
                if(not self.can_lynch):
                    self.can_lynch = True
    def kill(self, player):
        if(player.role_type == WW):
            self.num_ww-=1
        elif(player.role_type == VG):
            self.num_vg-=1
        player.status = DEAD
    def clear_votes(self):
        self.voted_players = {}
        for player in self.players:
            if(player.status == ALIVE):
                self.voted_players[player]=0


def save_contacts(contacts):
    file = open('contacts.txt','w') 
    for phone in contacts:
        file.write(phone) 
        file.write('#') 
        file.write(contacts[phone])
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


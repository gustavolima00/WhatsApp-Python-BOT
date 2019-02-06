import time
from datetime import datetime, timedelta
from random import randint
import emoji
import clipboard

def get_header(driver):
    return 'SLEEP'

def send_message(driver, username, text):
    print('=============')
    print('Enviando mensagem para:', username)
    print('Mensagem:', text)
    print('=============')
    return True


def send_text(driver, username ,texts, *args):
    try:
        arq_path = 'texts/' + texts.lower() + '.txt'
        arq = open(arq_path, 'r')
        text = arq.read()
        phrases = text.split('%')
        num = len(phrases)-1
        if(num == 0):
            send_message(driver, username, text)
            return
        if(len(args) != num):
            print('erro send_text')
            return
        arq.close()
        message = ''
        for x in range(0, num):
            message += phrases[x]+args[x]
        message += phrases[x + 1]
        send_message(driver, username, message)
    except FileNotFoundError:
        print('Texto não encontrado')


def find_user(driver, username):
    pass

def get_unread_chats(driver):
    chats = [] 
    text = input('Chats não lidos: ex. 123/321\n')
    numbers = text.split('/')
    for number in numbers:
        chats.append(number)
    return chats

GROUP = 1
NORMAL = 2
def get_messages(driver, chat_name):
    try:
        if(chat_name[0]=='+'):
            chat_type = NORMAL
        else:
            chat_type = GROUP
        if(chat_type == GROUP):
            messages_dict={}
            text2 = input('Mensagens: ex 123:alo/312:hello\n')
            all_messages = text2.split('/')     
            for message in all_messages:
                content = message.split(':')
                user = content[0]
                text = content[1]
                if(not user in messages_dict):
                    messages_dict[user]=[]
                messages_dict[user].append(text)
            return messages_dict
        elif(chat_type == NORMAL):
            text2 = input('Mensagens: ex alo/hello\n')
            messages = text2.split('/')
            messages_dict={}
            messages_dict[chat_name]=messages
            return messages_dict
        else:
            print('Entrada inválida')
            return
    except:
            print('Entrada inválida')
            return

# +1:iniciar/+2:entrar/+3:entrar/+4:entrar/+5:force/+5:entrar
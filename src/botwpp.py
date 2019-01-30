from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from random import randint
from selenium.webdriver.common.action_chains import ActionChains
import emoji
import clipboard

CHAT = '._2EXPL'
#SubClasse of Chat
UNREAD = '.CxUIE'

CHAT_FOCUSED = '._2EXPL._1f1zm'
END_BUTTON = '_298R6'
MESSAGE_TEXT = '._3zb-j.ZhF0n'
SEARCH_BOX = '_2MSJr'
SEARCH_CLOSE = 'C28xL'
MSG_BOX = '_1Plpp'
SEND_BUTTON = '_35EW6'
CHAT_TITLE = '._2zCDG'
NAME_IN_GROUP = '.RZ7GO'
NUM_MESSAGES = '._1mq8g'
# Class message
MESSAGE = '._3_7SH'
# Subclasses of message
TEXT = '._3DFk6'
PHOTO = '._3qMSo'
AUDIO = '._17oKL'
# Subclasses of tipes
MESSAGE_OUT = '.message-out'
MESSAGE_IN = '.message-in'
# subclasse of out and in
TAIL = '.tail'
# Example of css class
# MESSAGE_OUT_TAIL = '._3_7SH._3DFk6.message-out.tail'

def get_header(driver):
    try:
        header = driver.find_elements_by_css_selector(CHAT_TITLE)
        title = header[0].text
    except:
        title = ''
    return title

def send_message(driver, username, text):
    time.sleep(0.1)
    if(username != get_header(driver)):
        if(not find_user(driver, username)):
            print('Falha achar usuário')
            return False
    try:
        msg_box = driver.find_element_by_class_name(MSG_BOX)
        clipboard.copy(text)
        msg_box.send_keys(Keys.CONTROL, 'v')
        time.sleep(0.1)
        send_button = driver.find_element_by_class_name(SEND_BUTTON)
        send_button.click()
        return True
    except:
        print('Falha ao enviar mensagem')
        return False


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
    result = True
    try:
        search_box = driver.find_element_by_class_name(SEARCH_BOX)
        search_box.send_keys(username)
    except:
        print('Falha ao procurar conversa')
        result = False
    try:
        time.sleep(0.1)
        user = driver.find_element_by_xpath(
            '//span[@title = "{}"]'.format(username))
        user.click()
    except:
        print('Falha ao entrar na conversa')
        result = False  
    try:
        time.sleep(0.1)
        search_close = driver.find_element_by_class_name(SEARCH_CLOSE)
        search_close.click()
    except:
        print('Falha ao clicar no botao de voltar')
        result = False  
    return result
# Abre conversas não lidas
def get_unread_chats(driver):
    contents = driver.find_elements_by_css_selector(CHAT + UNREAD)
    chats = []
    for content in contents:
        name = content.text.split('\n')[0]
        chats.append(name)
    return chats

def get_messages(driver, chat_name):
    find_user(driver, chat_name)
    try:
        num_messages = driver.find_elements_by_css_selector(NUM_MESSAGES)
        num_messages = int(num_messages[0].text[0])
    except:
        return {}
    try:
        end_button = driver.find_element_by_class_name(END_BUTTON)
        end_button.click()
    except:
        pass
    messages_dict = {}
    messages = []
    contents = driver.find_elements_by_css_selector(MESSAGE+MESSAGE_IN)
    for content in contents[::-1][:num_messages]:
        content_style = '.' + content.get_attribute("class").replace(' ', '.')
        user_name = content.find_elements_by_css_selector(NAME_IN_GROUP)
        if(TEXT in content_style):
            message = content.find_elements_by_css_selector(MESSAGE_TEXT)
            message = message[0].text
        elif(PHOTO in content_style):
            message = 'PHOTO'
        elif(AUDIO in content_style):
            message = 'AUDIO'
        else:
            pass
        messages.append(message)
        if(len(user_name)!=0):
            user_name = user_name[0].text
            if(not user_name in messages_dict):
                messages_dict[user_name] = []
            for message in messages:
                messages_dict[user_name].append(message)
            messages.clear()
    if(messages_dict == {}):
        title = get_header(driver)
        messages_dict[title]=messages
    return messages_dict
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime, timedelta
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
SEARCH_CLOSE = '.gQzdc._3sdhb'
SEARCH_BUTTON = '.C28xL'
MSG_BOX = '_1Plpp'
SEND_BUTTON = '_35EW6'
CHAT_TITLE = '._3XrHh'
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
        header = driver.find_element_by_css_selector(CHAT_TITLE)
        title = header.text
    except:
        title = ''
    return title

def send_message(driver, username, text):
    time_now = datetime.now() 
    end_time = time_now + timedelta(seconds=10)
    # Escrevendo mensagem
    while True:
        time_now = datetime.now() 
        if(time_now>end_time):
            print("Erro em send_message, tempo limite excedido")
            return False
        try:
            # Achando usuário
            while True:
                time_now = datetime.now() 
                if(time_now>end_time):
                    print("Erro em send_message find_user, tempo limite excedido")
                    return False
                if(find_user(driver, username)):
                    break
            time.sleep(0.1)
            msg_box = driver.find_element_by_class_name(MSG_BOX)
            clipboard.copy(text)
            msg_box.send_keys(Keys.CONTROL, 'v')
            break
        except:
            pass
    # Enviando mensagem
    while True:
        time_now = datetime.now() 
        if(time_now>end_time):
            print("Erro em send_message click_button, tempo limite excedido")
            return False
        try:
            # Achando usuário
            send_button = driver.find_element_by_class_name(SEND_BUTTON)
            send_button.click()
        except:
            break    
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
    time_now = datetime.now() 
    end_time = time_now + timedelta(seconds=5)
    if(username == get_header(driver)):
        return True
    result = True
    # Fechando pesquisa anterior
    while True:
        time_now = datetime.now() 
        if(time_now>end_time):
            print("Erro em find_user, tempo limite excedido")
            return False      
        while True:
            time_now = datetime.now()
            if(time_now>end_time):
                print("Erro em find_user(back_button 1) tempo limite excedido")
                return False
            try:
                search_close = driver.find_element_by_css_selector(SEARCH_CLOSE)
                button = search_close.find_element_by_css_selector(SEARCH_BUTTON)
                button.click()
            except:
                break
        try:
            search_box = driver.find_element_by_class_name(SEARCH_BOX)
            search_box.send_keys(username)
        except:
            continue
        try:
            user = driver.find_element_by_xpath(
                '//span[@title = "{}"]'.format(username))
            user.click()
            if(username == get_header(driver)):
                while True:
                    time_now = datetime.now()
                    if(time_now>end_time):
                        print("Erro em find_user(back_button 2) tempo limite excedido")
                        return False
                    try:
                        search_close = driver.find_element_by_css_selector(SEARCH_CLOSE)
                        button = search_close.find_element_by_css_selector(SEARCH_BUTTON)
                        button.click()
                    except:
                        break
                break
        except:
            continue 
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
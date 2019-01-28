from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from random import randint
from selenium.webdriver.common.action_chains import ActionChains
import emoji
import clipboard

CHAT_NORMAL = '._2wP_Y'
CHAT_UNREAD = '._2EXPL.CxUIE'
CHAT_FOCUSED = '._2EXPL._1f1zm'
END_BUTTON = '_298R6'
MESSAGE_TEXT = '._3zb-j.ZhF0n'
SEARCH_BOX = '_2MSJr'
SEARCH_CLOSE = 'C28xL'
MSG_BOX = '_1Plpp'
SEND_BUTTON = '_35EW6'
CHAT_TITLE = '._2zCDG'
NAME_IN_GROUP = '.RZ7GO'
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

class Chat:
	def __init__(self, chat_type, name, qnt_messages):
		self.name = name
		self.chat_type = chat_type
		self.qnt_messages = int(qnt_messages)

def get_header(driver):
	header = driver.find_elements_by_css_selector(CHAT_TITLE)
	if(len(header)!=0):
		title = header[0].text
	else:
		title = ''
	return title



def send_message(driver, text):
    msg_box = driver.find_element_by_class_name(MSG_BOX)
    clipboard.copy(text)
    msg_box.send_keys(Keys.CONTROL, 'v')
    send_button = driver.find_element_by_class_name(SEND_BUTTON)
    send_button.click()


def run_command(driver, command):
    arq_path = 'commands/' + command.lower() + '.txt'
    arq = open(arq_path, 'r')
    text = arq.read()
    phrases = text.split('#')
    num = len(phrases)
    arq.close()
    random_num = randint(0, num-1)
    message = phrases[random_num]
    send_message(driver, message)


def send_text(driver, texts, *args):
    try:
        arq_path = 'texts/' + texts.lower() + '.txt'
        arq = open(arq_path, 'r')
        text = arq.read()
        phrases = text.split('%')
        num = len(phrases)-1
        if(num == 0):
            send_message(driver, text)
            return
        if(len(args) != num):
            print('erro send_text')
            return
        arq.close()
        message = ''
        for x in range(0, num):
            message += phrases[x]+args[x]
        message += phrases[x + 1]
        send_message(driver, message)
    except FileNotFoundError:
        print('Texto não encontrado')


def find_user(driver, username):
    search_box = driver.find_element_by_class_name(SEARCH_BOX)
    search_box.send_keys(username)
    time.sleep(1)
    try:
        user = driver.find_element_by_xpath(
            '//span[@title = "{}"]'.format(username))
        user.click()
        search_close = driver.find_element_by_class_name(SEARCH_CLOSE)
        search_close.click()
    except:
        print('Falha ao entrar na conversa')

# Abre conversas não lidas


def get_chats(driver):
    contents = driver.find_elements_by_css_selector(CHAT_UNREAD)
    chats = []
    for content in contents:
        unread_chat = content.text.split('\n')
        tam = len(unread_chat)
        print('tam', tam)
        print('unread_chat', unread_chat)
        name = unread_chat[0]
        if(tam == 4 and unread_chat[3].isdigit()):
            chat_type = 'normal'
            num = unread_chat[3]
        elif(tam == 5 and unread_chat[4].isdigit()):
            chat_type = 'group'
            num = unread_chat[4]
        else:
            chat_type = 'unknow'
            num = 0
        chat = Chat(chat_type, name, num)
        chats.append(chat)
    return chats

def get_messages(driver, num):
	try:
		end_button = driver.find_element_by_class_name(END_BUTTON)
		end_button.click()
	except:
		pass
	messages_dict = {}
	messages = []
	contents = driver.find_elements_by_css_selector(MESSAGE+MESSAGE_IN)
	for content in contents[::-1][:num]:
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
		print('message', message)
		messages.append(message)
		if(len(user_name)!=0):
			user_name = user_name[0].text
			print('user_name', user_name)
			if(not user_name in messages_dict):
				messages_dict[user_name] = []
			for message in messages:
				messages_dict[user_name].append(message)
			messages.clear()
			#messages.clear()
	if(messages_dict == {}):
		title = get_header(driver)
		messages_dict[title]=messages
	return messages_dict
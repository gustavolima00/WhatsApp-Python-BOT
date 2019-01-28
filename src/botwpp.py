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
MESSAGE = '._3zb-j.ZhF0n'
SEARCH_BOX = '_2MSJr'
SEARCH_CLOSE = 'C28xL'
MSG_BOX = '_1Plpp'
SEND_BUTTON = '_35EW6'
CHAT_TITLE = '_2zCDG'
class Chat:
	def __init__(self, chat_type, name, qnt_messages):
		self.name = name
		self.chat_type = chat_type
		self.qnt_messages = int(qnt_messages)

def send_message(driver, text):
	msg_box = driver.find_element_by_class_name(MSG_BOX)
	clipboard.copy(text)
	msg_box.send_keys(Keys.CONTROL, 'v')
	send_button = driver.find_element_by_class_name(SEND_BUTTON)
	send_button.click()

def run_command(driver, command):
	try:
		arq_path = 'commands/' + command.lower() + '.txt'
		arq = open(arq_path, 'r')
		text = arq.read()
		phrases = text.split('#')
		num = len(phrases)
		arq.close()
		random_num = randint(0, num-1)
		message = phrases[random_num]
		send_message(driver, message)
	except FileNotFoundError:
		print('Comando não encontrado')


def find_user(driver, username):
	search_box = driver.find_element_by_class_name(SEARCH_BOX)
	search_box.send_keys(username)
	time.sleep(1)
	try:
		user = driver.find_element_by_xpath('//span[@title = "{}"]'.format(username))	
		user.click()
		search_close = driver.find_element_by_class_name(SEARCH_CLOSE)
		search_close.click()
	except:
		print('Falha ao entrar na conversa')

#Abre conversas não lidas
def get_chats(driver):
	contents = driver.find_elements_by_css_selector(CHAT_UNREAD)
	chats = []
	for content in contents:
		unread_chat = content.text.split('\n')
		tam = len(unread_chat)
		print('tam', tam)
		print('unread_chat', unread_chat)
		name =  unread_chat[0]
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
	#Scroll Down
	try:
		end_button = driver.find_element_by_class_name(END_BUTTON)
		end_button.click()
	except:
		pass

	contents = driver.find_elements_by_css_selector(MESSAGE)
	messages = []
	i=0
	for content in contents[::-1]:
		if( not i<num):
			break
		message = content.text.split('\n')
		messages.append(message[0])
		i+=1
		
		
	return messages


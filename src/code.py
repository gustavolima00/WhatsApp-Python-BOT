from selenium import webdriver
from botwpp import *
from datetime import datetime
import time
from selenium.common.exceptions import NoSuchElementException

#Abrindo mensagem inicial
help_arq = open('help_text.txt', 'r')
help_text = help_arq.read()

driver = webdriver.Chrome()
driver.get('https://web.whatsapp.com/')
input('Insira o QR e aperte enter')

while True:
	try:
		chats = get_chats(driver)
		for chat in chats:
			find_user(driver, chat.name)
			print('Numero/Titulo do grupo:', chat.name)
			print('Tipo de conversa:', chat.chat_type)
			print('Número de mensagens não lidas:', chat.qnt_messages)
			time.sleep(1)
			messages = get_messages(driver, chat.qnt_messages)
			print('Mensagens:', messages)
			
			for message in messages:
				if(message == '/help'):
					send_message(driver, help_text)
				elif(message == '/joke'):
					send_joke(driver)
				elif(message == '/startwerewolf'):
					send_message(driver, 'Função não disponível')
				elif(message == '/helpwerewolf'):
					send_message(driver, 'Função não disponível')
	except NoSuchElementException:
		pass




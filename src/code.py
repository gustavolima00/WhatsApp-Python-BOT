from selenium import webdriver
from botwpp import *
from datetime import datetime
import time
from selenium.common.exceptions import NoSuchElementException

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome('chromedriver', service_args=["--verbose", "--log-path=/tmp/CHROMIUM_LOG"], options=chrome_options)
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
				if(message[0] == '/'):
					print('Rodando comando:', message[1:])
					try:
						run_command(driver, message[1:])
					except FileNotFoundError as error:
						print('Peguei um erro', error)
	except NoSuchElementException:
		pass




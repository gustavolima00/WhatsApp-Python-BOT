from selenium import webdriver
from botwpp import *
from datetime import datetime
import time
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime, timedelta

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome('chromedriver', service_args=["--verbose", "--log-path=/tmp/CHROMIUM_LOG"], options=chrome_options)
driver.get('https://web.whatsapp.com/')
input('Insira o QR e aperte enter')

is_running = False
group_name = ''
end_time = None

while True:
	if(is_running):
		time_now = datetime.now()
		if(time_now > end_time):
			find_user(driver, group_name)
			send_message(driver, 'O jogo acabou')
			is_running = False
			group_name = ''
			end_time = None
	try:
		chats = get_chats(driver)
		for chat in chats:
			find_user(driver, chat.name)
			time.sleep(1)
			messages = get_messages(driver, chat.qnt_messages)

			print('Numero/Titulo do grupo:', chat.name)
			print('Tipo de conversa:', chat.chat_type)
			print('Número de mensagens não lidas:', chat.qnt_messages)
			print('Mensagens:', messages)
			
			for message in messages:
				if(message.lower() == 'startgame'):
					if(chat.chat_type == 'group'):
						time_now = datetime.now()
						end_time = time_now + timedelta(minutes=1)
						group_name = chat.name
						is_running = True
						send_message(driver, 'O jogo começou, em 1 minuto fecha')

					else:
						send_message(driver, 'Comando permitido apenas em grupos')
				else:
					run_command(driver, message)

	except NoSuchElementException:
		pass




default:
	cd src && python3 main.py
build:
	apt-get install xsel
	apt-get install xclip
	pip install -r requirements.txt	
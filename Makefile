default:
	cd src && python3 code.py
build:
	apt-get install xsel
	apt-get install xclip
	pip install -r requirements.txt	
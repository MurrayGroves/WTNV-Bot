import os
import threading

def bootBot():
	if os.name == 'nt':
		os.system('py bootbot.py')
	else:
		os.system('python bootbot.py')

def loopBot():
	if os.name == 'nt':
		os.system('py loopbotstart.py')
	else:
		os.system('python loopbotstart.py')

botThread = threading.Thread(name='botThread', target=bootBot)
loopThread = threading.Thread(name='loopThread', target=loopBot)

botThread.start()
loopThread.start()

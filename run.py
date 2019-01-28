import os
import threading

def bootBot():
	os.system('py bootbot.py')

def loopBot():
	os.system('py loopbotstart.py')

botThread = threading.Thread(name='botThread', target=bootBot)
loopThread = threading.Thread(name='loopThread', target=loopBot)

botThread.start()
loopThread.start()

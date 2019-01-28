import os
import threading

def bootBot():
	try:
		os.system('py bootbot.py')
	except:
		os.system('python bootbot.py')

def loopBot():
	try:
		os.system('py loopbotstart.py')
	except:
		os.system('python loopbotstart.py')

botThread = threading.Thread(name='botThread', target=bootBot)
loopThread = threading.Thread(name='loopThread', target=loopBot)

botThread.start()
loopThread.start()

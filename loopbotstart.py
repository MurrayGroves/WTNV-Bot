import os
import time
from loopbot import WTNVBot
if os.path.isdir("data/") == False:
	print("Creating data directory")
	os.mkdir("data/")

try:
	f = open("data/token.data", "r")
	f.close()

except:
	f = open("data/token.data", "w+")
	token = input("No token found, please input token:\n")
	f.write(token)
	f.close()
	print("Token saved")
	time.sleep(1)

print("Booting...")

b = WTNVBot()
b.run()

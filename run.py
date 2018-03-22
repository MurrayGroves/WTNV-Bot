import os
from bot import WTNVBot
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

if os.path.isfile("data/latestEp.data") == False:
	print("Creating episode file")
	open("data/latestEp.data", "w+")

if os.path.isfile("data/channel.data") == False:
	channel = input("Enter channel ID of announcements:\n")
	print("Creating channel file")
	open("data/channel.data", "w+")
	f.close()

if os.path.isfile("data/announcement.data") == False:
	announcement = input("Enter announcement message:\n")
	print("Creating announcement file")
	open("data/announcement.data", "w+")
	
print("Booting...")

b = WTNVBot()
b.run()

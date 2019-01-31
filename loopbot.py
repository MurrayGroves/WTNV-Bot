import discord
import asyncio

import os
import sys
import inspect
import time
import random
import podcastparser
import urllib.request
import json
import _thread
import threading

from datetime import datetime

global os_name

#Platform check
if os.name == "nt":
    print("Windows detected")
    os_name = "windows"

elif os.name == "posix":
    print("Unix detected")
    os_name = "unix"
else:
    print("Unknown OS, Only Unix and Windows are supported.")

    #Set OS to none, causing program to ask for OS
    os_name = ''

    #While OS is not windows or unix, ask for OS
    while os_name != 'windows' and os_name != 'unix':
        #Ask for OS and make sure is string to prevent errors
        choice = str(input('Please choose compatibility mode to use:(windows/unix)'))
        #Check input
        if choice.lower() == 'windows':
            os_name = 'windows'
        elif choice.lower() == 'unix':
            os_name = "unix"
        else:
            os_name = ''


#Discord Setup
class WTNVBot(discord.Client):
    def __innit__(self):
        self.th = Thread(target=self.check, args=(self))
        global shard_count
        version = "1.0"
        self.token()
        self.appinfo = ""
        self.owner = ""
        self.prefix = "<"
        super().__innit__(shard_id=0, shard_count=1)
        self._setup_logging()
        self.aiosession = aiohttp.ClientSession(loop=self.loop)

    global meme
    def run(self):
        global meme
        meme = self
        token = open("data/token.data", "r").read()
        token = token.replace("\n", "")
        loop = asyncio.get_event_loop()
        self.loop = loop
        try:
            loop.run_until_complete(self.start(token))
        finally:
            try:
                try:
                    self.loop.run_until_complete(self.logout())
                except:
                    pass
                pending = asyncio.Task.all_tasks()
                gathered = asyncio.gather(*pending)
                try:
                    gathered.cancel()
                    loop.run_until_complete(gathered)
                    gathered.exception()
                except:
                    pass
            except Exception as e:
                loop.close()

    async def cmd_boop(self,message):
        await self.send_message(message.channel,'flip')
        print('flip')

    async def on_ready(self):
        # Boot logging
        self.appinfo = await self.application_info() #you can now get ALL your appinfo ##http://discordpy.readthedocs.io/en/latest/api.html#discord.AppInfo
        self.owner = self.appinfo.owner #you now always have an accurate owner object to use (this is a user object, e.g. self.owner.id, self.owner.name etc.
        now = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("Connected as " + str(self.user) + " at " + now + " on " + str(len(self.servers)) + " servers!")

        while True:
            jdata = open('data/commands.json').read()
            jdata = json.loads(jdata)

            json_keys = []
            for key in jdata:
                json_keys.append(key)

            choice = random.choice(json_keys)
            choice_answer = jdata[choice]

            game = (discord.Game(name=choice+' : '+choice_answer, type=0))
            await self.change_presence(game=game)

            feedurl = 'http://feeds.nightvalepresents.com/welcometonightvalepodcast'
            parsed = podcastparser.parse(feedurl, urllib.request.urlopen(feedurl), max_episodes=1)

            try:
                open('data/latestEp.data')

            except:
                open('data/latestEp.data', 'w+')

            if str(parsed) not in open("data/latestEp.data", "r"):
                f = open("data/latestEp.data", "w")
                f.write(str(parsed))
                f.close()
                feedurl = 'http://feeds.nightvalepresents.com/welcometonightvalepodcast'
                parsed = podcastparser.parse(feedurl, urllib.request.urlopen(feedurl), max_episodes=1)

                global os_name

                if os_name == 'windows':
                    # parsed is a dict
                    episode = parsed.get("episodes", "none")
                    title = parsed.get("channel", "none")
                    msg = str(episode[0])

                    msg = msg.replace("{'description': ", "")
                    desc,link  = msg.split('.com', 1)
                    bin,link = link.split("'link': '", 1)
                    del bin
                    link, title = link.split("',", 1)
                    bin,title = title.split("'title': ")
                    del bin
                    title,bin = title.split("', 'subtitle'")
                    del bin
                    title = title.replace("'", "", 1)

                    msg = desc.replace("\\n", " ")
                    msg = msg.replace("'", "", 1)
                    msg = msg + ".com"
                    msg, weather = msg.split("Weather: ")
                    weather = " " + weather
                    weather, author = weather.split(' by ')
                    print(author)
                    bin,author = author.split("   ")
                    del bin
                    author = "https://" + author

                    em = discord.Embed(title=title, colour=random.randint(0, 16777215))
                    em.add_field(name="Description", value=msg+'"')
                    em.add_field(name="Weather", value=weather)
                    em.add_field(name="Weather Author", value=author)
                    em.add_field(name="Link", value=link)
                    channel = discord.Object(id=220959090673844226)
                    try:
                        content = open("data/announcement.data").read()

                    except:
                        open('data/announcement.data','w+')
                    await self.send_message(channel, str(content))
                    await self.send_message(channel, embed=em)
                    print('uwu')

                else:
                    content = parsed['episodes']
                    content = content[0]

                    description = content['description']
                    desc_html = content['description_html']
                    description,desc_html = desc_html.split('</p>\n\n',1)
                    description = description.replace('<p>','')
                    desc_html = desc_html.replace('<p>Weather: ','',2)

                    weather,desc_html = desc_html.split('</p>',1)
                    print(weather)
                    weather_name,weather = weather.split('”',1)
                    weather_name = weather_name.replace('“','')

                    weather_author = weather.replace(' <br>','')
                    weather_author = weather_author.replace(' by ','')
                    weather_author,desc_html = weather_author.split('<a href="',1)
                    weather_link,desc_html = desc_html.split('"',1)


                    desc_html = desc_html.replace('\n\n', '')

                    enclosures = content['enclosures']
                    enclosures = enclosures[0]
                    #time = enclosures['time']
                    url = enclosures['url']

                    title = url.split('/',8)[-1]
                    title = title.replace('_',' ')
                    title = title.replace(' i.mp3','')

                    print('Title:{}, Desc:{},Weather:{}, Weather Author:{}, Weather Link: {}'.format(title,description,weather_name,weather_author,weather_link))


                    em = discord.Embed(title=title, colour=random.randint(0, 16777215))
                    em.add_field(name="Description", value=description)
                    em.add_field(name="Weather", value=weather_name)
                    em.add_field(name="Weather Author", value=weather_author)
                    em.add_field(name="Link", value=weather_link)
                    channel = discord.Object(id=220959090673844226)

                    try:
                        content = open("data/announcement.data").read()

                    except:
                        open('data/announcement.data','w+')
                        await self.send_message(channel, str(content))

                    await self.send_message(channel, embed=em)








            await asyncio.sleep(60)

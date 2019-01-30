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

    async def on_message(self, message):
        #Set content to be the content of the message
        msg = message.content
        content = message.content.strip()
        content = content.replace("<", "")

        if msg.startswith("<") == False:
            return

        command, *args = message.content.split(
            ' ')  # Uh, doesn't this break prefixes with spaces in them (it doesn't, config parser already breaks them)
        command = command[len('<'):].lower().strip()
        handler = getattr(self, 'cmd_' + command, None)
        if not handler:
            return
        print("{0.id}/{0!s}: {1}".format(message.author, message.content.replace('\n', '\n... ')))
        argspec = inspect.signature(handler)
        params = argspec.parameters.copy()
        sentmsg = response = None
        # noinspection PyBroadException
        #try:
        handler_kwargs = {}
        if params.pop('message', None):
            handler_kwargs['message'] = message
        if params.pop('channel', None):
            handler_kwargs['channel'] = message.channel
        if params.pop('author', None):
            handler_kwargs['author'] = message.author
        if params.pop('server', None):
            handler_kwargs['server'] = message.server
        if params.pop('permissions', None):
            handler_kwargs['permissions'] = user_permissions
        if params.pop('user_mentions', None):
            handler_kwargs['user_mentions'] = list(map(message.server.get_member, message.raw_mentions))
        if params.pop('channel_mentions', None):
            handler_kwargs['channel_mentions'] = list(map(message.server.get_channel, message.raw_channel_mentions))
        if params.pop('leftover_args', None):
            handler_kwargs['leftover_args'] = args
        args_expected = []
        for key, param in list(params.items()):
             # parse (*args) as a list of args
            if param.kind == param.VAR_POSITIONAL:
                handler_kwargs[key] = args
                params.pop(key)
                continue
            # parse (*, args) as args rejoined as a string
            # multiple of these arguments will have the same value
            if param.kind == param.KEYWORD_ONLY and param.default == param.empty:
                handler_kwargs[key] = ' '.join(args)
                params.pop(key)
                continue
            doc_key = '[{}={}]'.format(key, param.default) if param.default is not param.empty else key
            args_expected.append(doc_key)
            # Ignore keyword args with default values when the command had no arguments
            if not args and param.default is not param.empty:
                params.pop(key)
                continue
            # Assign given values to positional arguments
            if args:
                arg_value = args.pop(0)
                handler_kwargs[key] = arg_value
                params.pop(key)
        # Invalid usage, return docstring
        if params:
            docs = getattr(handler, '__doc__', None)
            if not docs:
                docs = 'Usage: {}{} {}'.format(
                    prefix,
                    command,
                    ' '.join(args_expected)
                )
            docs = dedent(docs)
            await self.safe_send_message(
                message.channel,
                '```\n{}\n```'.format(docs.format(command_prefix=prefix)),
                expire_in=60
            )
            return
        response = await handler(**handler_kwargs)
        if response and isinstance(response, Response):
            content = response.content
            if response.reply:
                content = '{}, {}'.format(message.author.mention, content)
            sentmsg = await self.safe_send_message(
                message.channel, content,
                expire_in=response.delete_after if self.config.delete_messages else 0,
                also_delete=message if self.config.delete_invoking else None
            )

    async def on_server_join(self, server):
        name = server.name
        msg = "Thanks for adding me to '{}', if you need help type <help , and have fun!".format(name)
        await self.send_message(server, msg)

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
                    channel = discord.Object(id=427145996284329985)
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
                    channel = discord.Object(id=427145996284329985)

                    try:
                        content = open("data/announcement.data").read()

                    except:
                        open('data/announcement.data','w+')
                        await self.send_message(channel, str(content))

                    await self.send_message(channel, embed=em)








            await asyncio.sleep(60)

import discord
import asyncio

import logging
logging.basicConfig(level=logging.INFO)


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

    async def cmd_set_message(self, channel, message, author):
        if author.id not in open("data/admins.data").read():
            em = discord.Embed(title="Set Message", colour=(random.randint(0, 16777215)))
            em.set_thumbnail(url="http://i.imgur.com/O4USCUs.png")
            em.add_field(name="You are inferior",value="The SSP have noted your superiority complex.", inline=True)
            await self.send_message(channel, embed=em)
            return

        content = message.content.strip()
        content = content.replace("<set_message", '')
        f = open("data/announcement.data", "w")
        f.write(content)
        f.close()

        em = discord.Embed(title='Announcment message set', colour=random.randint(0,16777215))


    async def cmd_latest(self, channel):
        feedurl = 'http://feeds.nightvalepresents.com/welcometonightvalepodcast'
        parsed = podcastparser.parse(feedurl, urllib.request.urlopen(feedurl), max_episodes=1)

        global os_name

        if os_name == 'windows':
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
            bin,author = author.split("   ")
            del bin
            author = "https://" + author

            em = discord.Embed(title=title, colour=random.randint(0, 16777215))
            em.add_field(name="Description", value=msg+'"')
            em.add_field(name="Weather", value=weather)
            em.add_field(name="Weather Author", value=author)
            em.add_field(name="Link", value=link)

            await self.send_message(channel, embed=em)


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

            em = discord.Embed(title=title, colour=random.randint(0, 16777215))
            em.add_field(name="Description", value=description)
            em.add_field(name="Weather", value=weather_name)
            em.add_field(name="Weather Author", value=weather_author)
            em.add_field(name="Link", value=weather_link)
            await self.send_message(channel, embed=em)

    async def cmd_learn(self, channel, message):
        msg = message.content.strip()
        msg = msg.replace("<learn ", "")
        msg = msg.replace("'", """<wack/this/is/an/apostrophe>""")
        try:
            msg,answer  = msg.split("*", 1)
        except ValueError:
            em = discord.Embed(title="Incorrect Formatting, please format <learn like this: <learn command*Answer")
            await self.send_message(channel, embed=em)
            return
        msg = msg.lower()
        old = open("data/commands.json").read()
        old = json.loads(old)
        old[msg] = answer
        json.dump(old, open('data/commands.json', 'w'))
        em = discord.Embed(title="Command Learned", colour=random.randint(0, 16777215))
        await self.send_message(channel, embed=em)

    async def cmd_unlearn(self, channel, message):
        msg = message.content.strip()
        msg = msg.replace("<unlearn ", "")
        msg = msg.lower()

        old = json.loads(open('data/commands.json').read())

        if msg in old:
            del old[msg]

        new = json.dumps(old)
        f = open('data/commands.json','w')
        f.write(new)
        f.close()

        em = discord.Embed(title="Command Unlearned", colour=random.randint(0, 16777215))
        await self.send_message(channel, embed=em)

    async def cmd_commands(self, channel):
        commands = open("data/commands.json", "r").read()
        commands = json.loads(commands)
        commands = str(commands.keys())
        commands = commands.replace("dict_keys([", "")
        commands = commands.replace("])", "")
        commands = commands.replace("'", "")
        commands = '`' + commands +'`'
        commands = commands.replace(",", "` , `")
        print(commands)
        em = discord.Embed(title=commands, colour=random.randint(0, 16777215))
        await self.send_message(channel, commands)

    async def cmd_ping(self, channel):
        t1 = time.perf_counter()
        await self.send_typing(channel)
        t2 = time.perf_counter()
        ping = (float(t2 - t1)) * 1000
        ping = round(ping, 0)
        ping = str(ping)
        ping = ping.replace(".0", "")
        em = discord.Embed(title="Ping", colour=(random.randint(0, 16777215)))
        em.set_thumbnail(url="http://i.imgur.com/L6sA5sd.png")
        em.add_field(name="Response time", value="{} ms.".format(ping), inline=True)
        await self.send_message(channel, embed=em)

    async def on_member_join(self, member):
        em = discord.Embed(title='***SECRET POLICE WARNING***',colour=16711680)
        em.set_thumbnail(url='https://www.clipartmax.com/png/middle/24-249770_red-triangle-exclamation-mark.png')
        em.add_field(name='Warning Message:', value='INTERLOPER!!!')

        channel = discord.Object(id=220959090673844226)

        await self.send_message(channel, embed=em)

    async def on_message(self, message):
        #Set content to be the content of the message
        msg = message.content
        content = message.content.strip()
        content = content.replace("<", "")

        if content.lower() in open("data/commands.json", "r").read():
            if message.author.id == '588822050710356006':
                print('No')
                return
            try:
                parsed = json.loads(open("data/commands.json", "r").read())
                reply = parsed[content.lower()]
                reply = reply.replace('<wack/this/is/an/apostrophe>',"'")
                await self.send_message(message.channel, reply)

            except:
                pass

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

import irc.client
import threading
from twitch_keywords.config import TWITCH_NICKNAME, TWITCH_OAUTH_TOKEN

class TwitchChatListener:
    def __init__(self, channel, keyword_callback):
        self.channel = channel.lower() if not channel.startswith('#') else channel.lower()
        self.keyword_callback = keyword_callback
        self.server = 'irc.chat.twitch.tv'
        self.port = 6667
        self.reactor = irc.client.Reactor()
        self.connection = None
        self.thread = None

    def on_connect(self, connection, event):
        print(f"已连接到 Twitch IRC: {self.channel}")
        connection.join(self.channel)

    def on_message(self, connection, event):
        user = event.source.split('!')[0]
        message = event.arguments[0]
        # 触发关键词回调
        self.keyword_callback(user, message)

    def start(self):
        self.connection = self.reactor.server().connect(
            self.server, 
            self.port, 
            nickname=TWITCH_NICKNAME,
            password=TWITCH_OAUTH_TOKEN
        )
        self.connection.add_global_handler("welcome", self.on_connect)
        self.connection.add_global_handler("privmsg", self.on_message)
        
        self.thread = threading.Thread(target=self.reactor.process_forever)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        if self.connection:
            self.connection.disconnect()
        if self.thread:
            self.thread.join()

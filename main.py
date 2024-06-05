from telethon import TelegramClient
# from telethon.tl.custom import Button
import configparser

import Bot.bot_handlers as basic_handlers

config = configparser.ConfigParser()
configPath = "config.ini"
config.read(configPath)

api_id = int(config.get('default', 'api_id'))
api_hash = config.get('default', 'api_hash')
BOT_TOKEN = config.get('default', 'BOT_TOKEN')

bot_session = "bot"

client = TelegramClient(bot_session, api_id, api_hash).start(bot_token=BOT_TOKEN)

if __name__ == '__main__':
    print("bot started")

    client.add_event_handler(basic_handlers.start_handler)
    client.add_event_handler(basic_handlers.help_handler)
    client.add_event_handler(basic_handlers.text_translate_handler)
    client.add_event_handler(basic_handlers.stop_handler)
    client.add_event_handler(basic_handlers.voice_translate_handler)

    client.run_until_disconnected()

# Telethon utility #pip install telethon
from telethon import TelegramClient, events
from telethon.tl.custom import Button

import configparser  # Library for reading from a configuration file, # pip install configparser

from info.message import MyMessage
from info.button import MyButton

#### Access credentials
config = configparser.ConfigParser()  # Define the method to read the configuration file
config.read('config.ini')  # read config.ini file

api_id = config.get('default', 'api_id')  # get the api id
api_hash = config.get('default', 'api_hash')  # get the api hash
BOT_TOKEN = config.get('default', 'BOT_TOKEN')  # get the bot token

# Create the client and the session called session_master. We start the session as the Bot (using bot_token)
client = TelegramClient('sessions/session_master', api_id, api_hash).start(bot_token=BOT_TOKEN)


@client.on(events.NewMessage(pattern='/(?i)start'))
async def start(event):
    sender = await event.get_sender()
    SENDER = sender.id
    await client.send_message(SENDER, MyMessage.text_start, parse_mode="HTML", buttons=MyButton.start_buttons)


@client.on(events.CallbackQuery(data="button_telegram_chanel_news"))
async def button_telegram_chanel_news(event):
    sender = await event.get_sender()
    SENDER = sender.id

    # Редактируем сообщение, удаляя кнопку
    await event.edit(buttons=None)

    await client.send_message(SENDER, MyMessage.text_telegram_chanel_news, parse_mode="HTML", buttons=MyButton.news_change_buttons)


@client.on(events.CallbackQuery(data="button_news_change"))
async def button_news_change(event):
    sender = await event.get_sender()
    SENDER = sender.id

    # Редактируем сообщение, удаляя кнопку
    await event.edit(buttons=None)

    button1 = Button.inline("1️⃣", data="button_character_1")
    button2 = Button.inline("2️⃣", data="button_character_2")
    button3 = Button.inline("3️⃣", data="button_character_3")
    button4 = Button.inline("4️⃣", data="button_character_4")
    button5 = Button.inline("Приступить к новостям", data="button_character_change")

    await client.send_message(SENDER, MyMessage.text_news_change, parse_mode="HTML", buttons=[[button1, button2, button3, button4], [button5]])

@client.on(events.CallbackQuery(data="button_website_news"))
async def button_website_news(event):
    sender = await event.get_sender()
    SENDER = sender.id

    # Редактируем сообщение, удаляя кнопку
    await event.edit(buttons=None)

    button1 = Button.inline("1️⃣", data="button_news_1")
    button2 = Button.inline("2️⃣", data="button_news_2")
    button3 = Button.inline("3️⃣", data="button_news_3")
    button4 = Button.inline("4️⃣", data="button_news_4")
    button5 = Button.inline("Закончать выбор", data="button_news_change")

    await client.send_message(SENDER, MyMessage.text_website_news, parse_mode="HTML", buttons=[[button1, button2, button3, button4],[button5]])

# Define the /help command
@client.on(events.NewMessage(pattern='/(?i)help'))
async def help(event):
    sender = await event.get_sender()
    SENDER = sender.id
    await client.send_message(SENDER, MyMessage.text_help, parse_mode="HTML")


def press_event(user_id):
    return events.CallbackQuery(func=lambda e: e.sender_id == user_id)


if __name__ == '__main__':
    print("bot started")
    client.run_until_disconnected()

# Telethon utility #pip install telethon
from telethon import TelegramClient, events
from telethon.tl.custom import Button

import configparser  # Library for reading from a configuration file, # pip install configparser

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
    text = "<b>AIST NEWS готов к работе!</b> ✉️\n\n" + \
           "Сейчас, для успешного использования бота далее, выбери из каких ресурсов, вы хотите фильтровать и получать новости? \n\n" + \
           "<b>/help</b> → У тебя возникли некоторые вопросы? Не переживай! Отправляй команду и получай подробную информацию о боте🧡"
    button1 = Button.inline("Telegram каналы", data="button_telegram_chanel_news")
    button2 = Button.inline("Новостные сайты", data="button_website_news")
    await client.send_message(SENDER, text, parse_mode="HTML", buttons=[button1, button2])


@client.on(events.CallbackQuery(data="button_telegram_chanel_news"))
async def button_telegram_chanel_news(event):
    sender = await event.get_sender()
    SENDER = sender.id

    # Редактируем сообщение, удаляя кнопку
    await event.edit(buttons=None)

    text = "Отправь в чат <b>ссылку</b> или <b>id</b> телеграмм канала, от которого хочешь получать новости!</b> 📨\n\n"+ \
           "<i>Возможен выбор нескольких критериев</i>\n"
    button1 = Button.inline("Закончить выбор", data="button_news_change")

    await client.send_message(SENDER, text, parse_mode="HTML", buttons=button1)


@client.on(events.CallbackQuery(data="button_news_change"))
async def button_news_change(event):
    sender = await event.get_sender()
    SENDER = sender.id

    # Редактируем сообщение, удаляя кнопку
    await event.edit(buttons=None)

    text = "<b>Выберите за какими новостями хотите следить:</b> \n\n" + \
           "  <b>1.</b> Россия\n" + \
           "  <b>2.</b> Мир\n" + \
           "  <b>3.</b> Спорт\n" + \
           "  <b>4.</b> Экономика\n\n"+ \
           "<i>Возможен выбор нескольких критериев</i>\n"
    button1 = Button.inline("1️⃣", data="button_character_1")
    button2 = Button.inline("2️⃣", data="button_character_2")
    button3 = Button.inline("3️⃣", data="button_character_3")
    button4 = Button.inline("4️⃣", data="button_character_4")
    button5 = Button.inline("Приступить к новостям", data="button_character_change")

    await client.send_message(SENDER, text, parse_mode="HTML", buttons=[[button1, button2, button3, button4], [button5]])

@client.on(events.CallbackQuery(data="button_website_news"))
async def button_website_news(event):
    sender = await event.get_sender()
    SENDER = sender.id

    # Редактируем сообщение, удаляя кнопку
    await event.edit(buttons=None)

    text = "<b>Выберите интернет ресурсы за которыми желаете следить:</b> \n\n" + \
           "<i>Описание ресурсов:</i>\n" + \
           "  <b>1.</b> Сайт 1 - описание\n" + \
           "  <b>2.</b> Сайт 2 - описание\n" + \
           "  <b>3.</b> Сайт 3 - описание\n" + \
           "  <b>4.</b> Сайт 4 - описание\n\n"+ \
           "<i>Возможен выбор нескольких критериев</i>\n"
    button1 = Button.inline("1️⃣", data="button_news_1")
    button2 = Button.inline("2️⃣", data="button_news_2")
    button3 = Button.inline("3️⃣", data="button_news_3")
    button4 = Button.inline("4️⃣", data="button_news_4")
    button5 = Button.inline("Закончать выбор", data="button_news_change")

    await client.send_message(SENDER, text, parse_mode="HTML", buttons=[[button1, button2, button3, button4],[button5]])

# Define the /help command
@client.on(events.NewMessage(pattern='/(?i)help'))
async def help(event):
    sender = await event.get_sender()
    SENDER = sender.id
    text = "<b>Подрбоная информация</b> 🤖️\n\n" + \
           "<i>Инструкция пользователя:</i>\n" + \
           "  <b>1.</b> Выберите нужное настроение \n" + \
           "  <b>2.</b> Выберите нужную категорию \n" + \
           "  <b>3.</b> Выберите откуда вы хотите извлекать новости и какие именно источники. \n" + \
           "  <b>4.</b> Наслаждайтесь пролистыванием новостей. \n\n" + \
           "<i>Техническая сторона проекта:</i>\n" + \
           "  <b>1.</b> Рекуррентные нейронные сети \n" + \
           "  <b>2.</b> Трансформеры \n" + \
           "  <b>3.</b> Использование обработчика/сборщика информаций с интернет ресурсов/telegram каналов \n\n" + \
           "<i>Бизнес решения проекта:</i>\n" + \
           "  <b>1.</b> Личный маскот \n" + \
           "  <b>2.</b> Возможность интеграций\n\n" + \
           "<i>Состав команды:</i>\n" + \
           "  <b>1.</b> Кашин Максим Игоревич \n" + \
           "  <b>2.</b> Жимолостнова Анна Васильевна \n" + \
           "  <b>3.</b> Поздняков Алексей Владимирович \n" + \
           "  <b>4.</b> Кузнецова Мария Павловна\n" + \
           "  <b>5.</b> Глушко Алиса Алексеевна \n" + \
           "  <b>6.</b> Разживин Александр Сергеевич\n" + \
           "  <b>7.</b> Калистратова Светлана Вячеславовна \n" + \
           "  <b>8.</b> Зюзин Сергей Александрович\n\n" + \
           "Узнал все, что хотел? Тогда пиши в чат → <b>/start</b> и узнавай что то новенькое🧡"
    await client.send_message(SENDER, text, parse_mode="HTML")


def press_event(user_id):
    return events.CallbackQuery(func=lambda e: e.sender_id == user_id)


if __name__ == '__main__':
    print("bot started")
    client.run_until_disconnected()

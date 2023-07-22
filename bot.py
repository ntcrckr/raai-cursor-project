from telethon.sync import TelegramClient
# from telethon.tl import types as tltypes
from telethon import events, custom
import config


class Bot:
    pass


async def start_handler(event: custom.Message):

    pass


if __name__ == "__main__":
    bot: TelegramClient
    with TelegramClient('bot', config.api_id, config.api_hash).start(bot_token=config.bot_token) as bot:
        bot.add_event_handler(
            start_handler,
            events.NewMessage(pattern='/start')
        )
        bot.run_until_disconnected()

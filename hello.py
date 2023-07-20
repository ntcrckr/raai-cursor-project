from telethon import TelegramClient
import config

with TelegramClient('anon', config.api_id, config.api_hash) as client:
    client.loop.run_until_complete(client.send_message('me', 'Hello, myself!'))

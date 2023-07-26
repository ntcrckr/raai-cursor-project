from telethon.sync import TelegramClient
# from telethon.tl import types as tltypes
from telethon import events, custom, Button
import config
from enum import Enum

from bot.info.message import MyMessage
from bot.info.button import MyButton
from database import Database, Emotion, Theme
import client


class UserState(Enum):
    none = 0
    waiting_channel = 1
    confirming_channel = 2


class Bot:
    user_state: dict[UserState] = {}
    bot: TelegramClient
    db: Database
    client: client.Client

    def __init__(self):
        self.db = Database()
        self.client = client.Client()
        self.bot = TelegramClient(
            'bot',
            config.api_id,
            config.api_hash
        ).start(
            bot_token=config.bot_token
        )
        _bot: TelegramClient
        with self.bot as _bot:
            _bot.add_event_handler(
                self.start,
                events.NewMessage(
                    pattern='/(?i)start'
                )
            )
            _bot.add_event_handler(
                self.button_telegram_chanel_news,
                events.CallbackQuery(
                    data="button_telegram_chanel_news"
                )
            )
            _bot.add_event_handler(
                self.button_news_change,
                events.CallbackQuery(
                    data="button_news_change"
                )
            )
            _bot.add_event_handler(
                self.button_website_news,
                events.CallbackQuery(
                    data="button_website_news"
                )
            )
            _bot.add_event_handler(
                self.help,
                events.NewMessage(
                    pattern='/(?i)help'
                )
            )
            _bot.add_event_handler(
                self.process_channel,
                events.NewMessage()
            )
            _bot.add_event_handler(
                self.button_channel_yes,
                events.CallbackQuery(
                    pattern="channel/yes/*"
                )
            )
            _bot.add_event_handler(
                self.button_channel_no,
                events.CallbackQuery(
                    pattern="channel/no"
                )
            )
            _bot.add_event_handler(
                self.emotions_change,
                events.CallbackQuery(
                    data="to_emotions"
                )
            )
            _bot.run_until_disconnected()

    async def start(self, event: custom.Message):
        sender = await event.get_sender()
        sender_id = sender.id
        existed = self.db.register_user(sender_id)
        if not existed:
            # TODO кидаем на новости
            pass
        else:
            await self.bot.send_message(
                sender_id,
                MyMessage.text_start,
                parse_mode="HTML",
                buttons=MyButton.start_buttons
            )
        raise events.StopPropagation

    async def button_telegram_chanel_news(self, event: events.callbackquery.CallbackQuery.Event):
        sender = await event.get_sender()
        sender_id = sender.id

        # Редактируем сообщение, удаляя кнопку
        await event.edit(buttons=None)

        # Получаем все каналы, связанные с пользователем
        channels = self.db.get_channels_by_user(sender_id)

        if channels:
            # Каналы найдены
            channel_info = "\n".join([f"{i+1}. {channel.link}" for i, channel in enumerate(channels)])
            message_text = f"Каналы, связанные с пользователем:\n{channel_info}"
        else:
            # Каналы не найдены
            message_text = "У пользователя нет связанных каналов."

        self.user_state[sender_id] = UserState.waiting_channel
        await self.bot.send_message(
            sender_id,
            message_text,
            parse_mode="HTML",
            buttons=[
                Button.inline(
                    "Перейти дальше",
                    data="to_emotions"
                )
            ]
        )

    # TODO
    async def button_news_change(self, event: events.callbackquery.CallbackQuery.Event):
        sender = await event.get_sender()
        sender_id = sender.id

        # Редактируем сообщение, удаляя кнопку
        await event.edit(buttons=None)

        await self.bot.send_message(
            sender_id,
            "Выбери нужные сайты: (не работает)",
            # parse_mode="HTML",
            # buttons=[
            #     Button.inline(
            #         "Перейти дальше",
            #         data="to_emotions"
            #     )
            # ]
        )

    async def process_channel(self, event: custom.Message):
        sender = await event.get_sender()
        sender_id = sender.id

        print(self.user_state)
        print(sender_id, type(sender_id))
        match self.user_state[sender_id]:
            case UserState.waiting_channel:
                if event.raw_text.find("t.me/") != -1 or event.raw_text[0] == "@":
                    if (event.raw_text[0] == "@"):
                        new_raw_text = event.raw_text.replace('@', 't.me/')
                    else:
                        new_raw_text = event.raw_text
                    channel = await self.client.get_channel_by_link(new_raw_text)
                    await self.bot.send_message(
                        sender_id,
                        f"Это нужный канал?\n@{channel.username}",
                        buttons=[
                            [
                                Button.inline("Да", data=f"channel/yes/{channel.id}/@{channel.username}"),
                                Button.inline("Нет", data="channel/no"),
                            ]
                        ]
                    )
                    self.user_state.pop(sender_id)
                else:
                    channel = await self.client.get_channel_by_name(event.raw_text)
                    await self.bot.send_message(
                        sender_id,
                        f"Это нужный канал?\n@{channel.username}",
                        buttons=[
                            [
                                Button.inline("Да", data=f"channel/yes/{channel.id}/@{channel.username}"),
                                Button.inline("Нет", data="channel/no"),
                            ]
                        ]
                    )
                    self.user_state.pop(sender_id)
            case _:
                print('lol')
        raise events.StopPropagation

    async def button_channel_yes(self, event: events.callbackquery.CallbackQuery.Event):
        sender = await event.get_sender()
        sender_id = sender.id
        channel_id = int(event.data.decode("utf-8").split('/')[-2])
        channel_link = event.data.decode("utf-8").split('/')[-1]
        # Редактируем сообщение, удаляя кнопку
        await event.edit(buttons=None)

        # print(channel_id, channel_link, type(channel_id), type(channel_link))
        connection_existed = self.db.add_channel_to_user(
            sender_id,
            channel_id,
            channel_link
        )
        if connection_existed:
            connection_existed = self.db.delete_user_to_channel(
                sender_id,
                channel_id
            )
            self.user_state[sender_id] = UserState.waiting_channel
            await self.bot.send_message(
                sender_id,
                f"Канал уже был добавлен! Следовательно, мы его удалили из твоих подписок\nПришли название канала, который хочешь добавить, или ссылку на него",
                parse_mode="HTML",
                buttons=[
                    Button.inline(
                        "Перейти дальше",
                        data="to_emotions"
                    )
                ]
            )
        else:
            self.user_state[sender_id] = UserState.waiting_channel
            await self.bot.send_message(
                sender_id,
                f"Канал добавлен!\nПришли название канала, который хочешь добавить, или ссылку на него",
                parse_mode="HTML",
                buttons=[
                    Button.inline(
                        "Перейти дальше",
                        data="to_emotions"
                    )
                ]
            )

    async def button_channel_no(self, event: events.callbackquery.CallbackQuery.Event):
        sender = await event.get_sender()
        sender_id = sender.id

        # Редактируем сообщение, удаляя кнопку
        await event.edit(buttons=None)

        self.user_state[sender_id] = UserState.waiting_channel
        await self.bot.send_message(
            sender_id,
            "Канал не добавлен\nПришли название канала, который хочешь добавить, или ссылку на него",
            parse_mode="HTML",
            buttons=[
                Button.inline(
                    "Перейти дальше",
                    data="to_emotions"
                )
            ]
        )

    # TODO
    async def button_website_news(self, event: events.callbackquery.CallbackQuery.Event):
        sender = await event.get_sender()
        sender_id = sender.id

        # Редактируем сообщение, удаляя кнопку
        await event.edit(buttons=None)

        button1 = Button.inline("1️⃣", data="button_news_1")
        button2 = Button.inline("2️⃣", data="button_news_2")
        button3 = Button.inline("3️⃣", data="button_news_3")
        button4 = Button.inline("4️⃣", data="button_news_4")
        button5 = Button.inline("Закончить выбор", data="button_news_change")

        await self.bot.send_message(
            sender_id,
            MyMessage.text_website_news,
            parse_mode="HTML",
            buttons=[
                [button1, button2, button3, button4],
                [button5]
            ]
        )

    # TODO
    async def emotions_change(self, event: events.callbackquery.CallbackQuery.Event):
        sender = await event.get_sender()
        sender_id = sender.id

        # Редактируем сообщение, удаляя кнопку
        await event.edit(buttons=None)

        user = self.db.get_user(sender_id)
        user_emotions = user.emotions.split('/')
        print(user_emotions)
        all_emotions = [Emotion.positive, Emotion.neutral, Emotion.negative]
        print([str(emotion) for emotion in all_emotions])

        await self.bot.send_message(
            sender_id,
            "Выберите нужные эмоции:",
            buttons=[
                [Button.inline(
                    f"{'✅' if str(emotion) in user_emotions else ''}{emotion}",
                    data=f"emotion/{emotion}"
                )]
                for emotion in all_emotions
            ]
        )

    async def help(self, event: custom.Message):
        sender = await event.get_sender()
        sender_id = sender.id
        await self.bot.send_message(
            sender_id,
            MyMessage.text_help,
            parse_mode="HTML"
        )
        raise events.StopPropagation


if __name__ == "__main__":
    Bot()

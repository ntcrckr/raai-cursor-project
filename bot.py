import aiogram.utils.exceptions
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config
import database
from client import Client
from database import Database, Emotion, Theme
import messages
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import stickers
import json
from models.Sentiment_and_theme import BertPredict


class States(StatesGroup):
    getting_channel = State()


class AistBot:
    bot: Bot
    client: Client
    database: Database
    storage: MemoryStorage
    dispatcher: Dispatcher
    user_message: dict = {}
    user_news: dict = {}
    user_mode: dict = {}
    models: BertPredict

    def __init__(self):
        self.bot = Bot(token=config.bot_token)
        self.client = Client()
        self.database = Database()
        self.storage = MemoryStorage()
        self.dispatcher = Dispatcher(self.bot, storage=self.storage)
        self.models = BertPredict(
            model_save_path_theme="./models/bert-theme.pth",
            model_save_path_sentim="./models/bert_sentiment_new.pth"
        )
        self.dispatcher.register_message_handler(
            self.start,
            commands=['start']
        )
        self.dispatcher.register_callback_query_handler(
            self.telegram_channel_news,
            lambda cq: cq.data == "telegram_channel_news"
        )
        self.dispatcher.register_message_handler(
            self.add_channel,
            state=States.getting_channel
        )
        self.dispatcher.register_callback_query_handler(
            self.confirm_yes,
            lambda cq: cq.data.find("confirm/yes") == 0
        )
        self.dispatcher.register_callback_query_handler(
            self.confirm_no,
            lambda cq: cq.data == "confirm/no"
        )
        self.dispatcher.register_callback_query_handler(
            self.website_news,
            lambda cq: cq.data == "website_news"
        )
        self.dispatcher.register_callback_query_handler(
            self.choose_website,
            lambda cq: cq.data.find("choose_website/") == 0
        )
        self.dispatcher.register_callback_query_handler(
            self.emotions,
            lambda cq: cq.data == "to_emotions",
            state="*"
        )
        self.dispatcher.register_callback_query_handler(
            self.choose_emotion,
            lambda cq: cq.data.find("choose_emotion/") == 0
        )
        self.dispatcher.register_callback_query_handler(
            self.themes,
            lambda cq: cq.data == "to_themes"
        )
        self.dispatcher.register_callback_query_handler(
            self.choose_theme,
            lambda cq: cq.data.find("choose_theme/") == 0
        )
        self.dispatcher.register_callback_query_handler(
            self.news,
            lambda cq: cq.data == "to_news"
        )
        self.dispatcher.register_callback_query_handler(
            self.send_news,
            lambda cq: cq.data == "news"
        )
        executor.start_polling(self.dispatcher, skip_updates=False)

    async def start(self, message: types.Message):
        existed = self.database.register_user(message.from_user.id)
        await message.answer_sticker(sticker=stickers.hello)
        if existed:
            await message.answer(**messages.start.copy())
        else:
            await message.answer(**messages.start_new.copy())

    async def telegram_channel_news(self, callback_query: types.CallbackQuery, state: FSMContext):
        self.user_mode[callback_query.from_user.id] = "channel"
        try:
            await callback_query.message.delete_reply_markup()
        except aiogram.utils.exceptions.MessageNotModified:
            pass
        channels = self.database.get_channels_by_user(callback_query.from_user.id)
        if channels:
            channels_text = "\n".join([
                f"{i + 1}. {channel.link}"
                for i, channel in enumerate(channels)
            ])
            text = f"Добавленные каналы:\n{channels_text}"
        else:
            text = "Добавленные каналы отсутствуют"
        msg = messages.ask_for_channel.copy()
        msg.text = f"{text}\n\n{msg.text}"
        await States.getting_channel.set()
        channel_message = await callback_query.message.answer(
            **msg
        )
        # await state.update_data(data={
        #     'channel_message_id': channel_message.message_id
        # })
        self.user_message[callback_query.from_user.id] = channel_message.message_id

    async def add_channel(self, message: types.Message, state: FSMContext):
        # state_data = await state.get_data()
        if message.text.find("t.me/") != -1 or message.text[0] == "@":
            await message.delete()
            channel = await self.client.get_channel_by_link(message.text)
            existed = self.database.add_channel_to_user(
                message.from_user.id,
                channel.id,
                f"@{channel.username}"
            )
            if not existed:
                channels = self.database.get_channels_by_user(message.from_user.id)
                if channels:
                    channels_text = "\n".join([
                        f"{i + 1}. {channel.link}"
                        for i, channel in enumerate(channels)
                    ])
                    text = f"Добавленные каналы:\n{channels_text}"
                else:
                    text = "Добавленные каналы отсутствуют"
                msg = messages.ask_for_channel.copy()
                msg.text = f"{messages.channel_added.text}\n{msg.text}\n\n{text}"
                await self.bot.edit_message_text(
                    chat_id=message.from_user.id,
                    message_id=self.user_message[message.from_user.id],
                    **msg
                )
            else:
                self.database.delete_user_to_channel(
                    message.from_user.id,
                    (await self.client.get_channel_by_link(message.text)).id
                )
                channels = self.database.get_channels_by_user(message.from_user.id)
                if channels:
                    channels_text = "\n".join([
                        f"{i + 1}. {channel.link}"
                        for i, channel in enumerate(channels)
                    ])
                    text = f"Добавленные каналы:\n{channels_text}"
                else:
                    text = "Добавленные каналы отсутствуют"
                msg = messages.ask_for_channel.copy()
                msg.text = f"{messages.channel_removed.text}\n\n{msg.text}\n\n{text}"
                await self.bot.edit_message_text(
                    chat_id=message.from_user.id,
                    message_id=self.user_message[message.from_user.id],
                    **msg
                )
        else:
            await state.finish()
            await message.delete()
            try:
                channel = await self.client.get_channel_by_name(message.text)
            except IndexError:
                channels = self.database.get_channels_by_user(message.from_user.id)
                if channels:
                    channels_text = "\n".join([
                        f"{i + 1}. {channel.link}"
                        for i, channel in enumerate(channels)
                    ])
                    text = f"Добавленные каналы:\n{channels_text}"
                else:
                    text = "Добавленные каналы отсутствуют"
                msg = messages.ask_for_channel.copy()
                msg.text = f"{messages.channel_not_found.text}\n{msg.text}\n\n{text}"
                await self.bot.edit_message_text(
                    chat_id=message.from_user.id,
                    message_id=self.user_message[message.from_user.id],
                    **msg
                )
                return
            channels = self.database.get_channels_by_user(message.from_user.id)
            if channels:
                channels_text = "\n".join([
                    f"{i + 1}. {channel.link}"
                    for i, channel in enumerate(channels)
                ])
                text = f"Добавленные каналы:\n{channels_text}"
            else:
                text = "Добавленные каналы отсутствуют"
            confirm_msg = messages.channel_confirmation.copy()
            confirm_msg.text = f"{confirm_msg.text}\n@{channel.username}\n\n{text}"
            confirm_msg.markup.inline_keyboard[0][0].callback_data += f"/{channel.id}/@{channel.username}"
            await self.bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=self.user_message[message.from_user.id],
                **confirm_msg
            )

    async def confirm_yes(self, callback_query: types.CallbackQuery, state: FSMContext):
        try:
            await callback_query.message.edit_reply_markup()
        except aiogram.utils.exceptions.MessageNotModified:
            pass
        channel_id = callback_query.data.split("/")[-2]
        channel_link = callback_query.data.split("/")[-1]
        self.database.add_channel_to_user(
            callback_query.from_user.id,
            channel_id,
            channel_link
        )
        channels = self.database.get_channels_by_user(callback_query.from_user.id)
        if channels:
            channels_text = "\n".join([
                f"{i + 1}. {channel.link}"
                for i, channel in enumerate(channels)
            ])
            text = f"Добавленные каналы:\n{channels_text}"
        else:
            text = "Добавленные каналы отсутствуют"
        msg = messages.ask_for_channel.copy()
        msg.text = f"{messages.channel_added.text}\n\n{text}\n\n{msg.text}"
        await States.getting_channel.set()
        await callback_query.message.edit_text(
            **msg
        )

    async def confirm_no(self, callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.message.edit_reply_markup()
        channels = self.database.get_channels_by_user(callback_query.from_user.id)
        if channels:
            channels_text = "\n".join([
                f"{i + 1}. {channel.link}"
                for i, channel in enumerate(channels)
            ])
            text = f"Добавленные каналы:\n{channels_text}"
        else:
            text = "Добавленные каналы отсутствуют"
        msg = messages.ask_for_channel.copy()
        msg.text = f"{messages.confirmation_no.text}\n\n{text}\n\n{msg.text}"
        await States.getting_channel.set()
        await callback_query.message.edit_text(
            **msg
        )

    async def website_news(self, callback_query: types.CallbackQuery):
        self.user_mode[callback_query.from_user.id] = "website"
        await callback_query.message.delete_reply_markup()
        websites = self.database.get_websites_by_user(callback_query.from_user.id)
        msg = messages.choose_websites.copy()
        emotions_button = msg.markup.inline_keyboard[0][0]
        new_msg = messages.Message(
            text=msg.text,
            markup_info=[
                (f"{'✅' if websites.tv1 else ''} Первый канал", "choose_website/tv1"),
                (f"{'✅' if websites.fon else ''} Фонтанка", "choose_website/fon"),
                (f"{'✅' if websites.rug else ''} Русская газета", "choose_website/rug"),
                (emotions_button.text, emotions_button.callback_data)
            ]
        )
        await callback_query.message.answer(
            **new_msg
        )

    async def choose_website(self, callback_query: types.CallbackQuery):
        websites = self.database.get_websites_by_user(callback_query.from_user.id)
        keyboard = callback_query.message.reply_markup.inline_keyboard
        match callback_query.data.split("/")[-1]:
            case "tv1":
                websites.tv1 = not websites.tv1
                self.database.session.commit()
                keyboard[0][0].text = f"{'✅' if websites.tv1 else ''} Первый канал"
            case "fon":
                websites.fon = not websites.fon
                self.database.session.commit()
                keyboard[1][0].text = f"{'✅' if websites.fon else ''} Фонтанка"
            case "rug":
                websites.rug = not websites.rug
                self.database.session.commit()
                keyboard[2][0].text = f"{'✅' if websites.rug else ''} Русская газета"
            case _:
                print("choose_website error")
        await callback_query.message.edit_reply_markup(
            types.InlineKeyboardMarkup(inline_keyboard=keyboard)
        )

    async def emotions(self, callback_query: types.CallbackQuery, state: FSMContext):
        await state.finish()
        user = self.database.get_user(callback_query.from_user.id)
        emotions = json.loads(user.emotions)
        msg = messages.choose_emotions.copy()
        themes_button = msg.markup.inline_keyboard[0][0]
        new_msg = messages.Message(
            text=msg.text,
            markup_info=[
                (f"{'✅' if Emotion.positive in emotions else ''} {Emotion.positive}",
                 f"choose_emotion/{Emotion.positive}"),
                (f"{'✅' if Emotion.neutral in emotions else ''} {Emotion.neutral}",
                 f"choose_emotion/{Emotion.neutral}"),
                (f"{'✅' if Emotion.negative in emotions else ''} {Emotion.negative}",
                 f"choose_emotion/{Emotion.negative}"),
                (themes_button.text, themes_button.callback_data)
            ]
        )
        try:
            await callback_query.message.edit_text(
                **new_msg
            )
        except aiogram.utils.exceptions.MessageNotModified:
            pass

    async def choose_emotion(self, callback_query: types.CallbackQuery):
        user = self.database.get_user(callback_query.from_user.id)
        emotions: list[Emotion] = json.loads(user.emotions)
        keyboard = callback_query.message.reply_markup.inline_keyboard
        match callback_query.data.split("/")[-1]:
            case Emotion.positive:
                if Emotion.positive in emotions:
                    emotions.remove(Emotion.positive)
                else:
                    emotions.append(Emotion.positive)
                user.emotions = json.dumps(emotions)
                self.database.session.commit()
                keyboard[0][0].text = f"{'✅' if Emotion.positive in emotions else ''} {Emotion.positive}"
            case Emotion.neutral:
                if Emotion.neutral in emotions:
                    emotions.remove(Emotion.neutral)
                else:
                    emotions.append(Emotion.neutral)
                user.emotions = json.dumps(emotions)
                self.database.session.commit()
                keyboard[1][0].text = f"{'✅' if Emotion.neutral in emotions else ''} {Emotion.neutral}"
            case Emotion.negative:
                if Emotion.negative in emotions:
                    emotions.remove(Emotion.negative)
                else:
                    emotions.append(Emotion.negative)
                user.emotions = json.dumps(emotions)
                self.database.session.commit()
                keyboard[2][0].text = f"{'✅' if Emotion.negative in emotions else ''} {Emotion.negative}"
            case _:
                print("choose_emotion error")
        await callback_query.message.edit_reply_markup(
            types.InlineKeyboardMarkup(inline_keyboard=keyboard)
        )

    async def themes(self, callback_query: types.CallbackQuery):
        user = self.database.get_user(callback_query.from_user.id)
        themes = json.loads(user.themes)
        msg = messages.choose_themes.copy()
        themes_button = msg.markup.inline_keyboard[0][0]
        new_msg = messages.Message(
            text=msg.text,
            markup_info=[
                *(
                    (
                        f"{'✅' if theme in themes else ''} {theme}",
                        f"choose_theme/{theme}"
                    )
                    for theme in database.all_themes
                ),
                (themes_button.text, themes_button.callback_data)
            ]
        )
        await callback_query.message.edit_text(
            **new_msg
        )

    async def choose_theme(self, callback_query: types.CallbackQuery):
        user = self.database.get_user(callback_query.from_user.id)
        themes: list[Theme] = json.loads(user.themes)
        keyboard = callback_query.message.reply_markup.inline_keyboard
        theme = callback_query.data.split("/")[-1]
        if Theme(theme) in themes:
            themes.remove(Theme(theme))
        else:
            themes.append(Theme(theme))
        user.themes = json.dumps(themes)
        self.database.session.commit()
        keyboard[database.all_themes.index(Theme(theme))][0].text = \
            f"{'✅' if Theme(theme) in themes else ''} {Theme(theme)}"
        try:
            await callback_query.message.edit_reply_markup(
                types.InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
        except aiogram.utils.exceptions.MessageNotModified:
            pass

    async def news(self, callback_query: types.CallbackQuery):
        if self.user_mode[callback_query.from_user.id] == "channel":
            await callback_query.message.answer_sticker(stickers.flying)
            msg = messages.processing_news.copy()
            await callback_query.message.edit_text(
                **msg
            )
            channels = self.database.get_channels_by_user(callback_query.from_user.id)
            self.user_news[callback_query.from_user.id] = list()
            for channel in channels:
                posts = await self.client.get_channel_messages(channel.id)
                async for post in posts:
                    self.user_news[callback_query.from_user.id].append(post)
            await self.send_news(callback_query=callback_query.from_user.id)
        elif self.user_mode[callback_query.from_user.id] == "website":
            await callback_query.message.answer_sticker(stickers.flying)
            msg = messages.processing_news.copy()
            await callback_query.message.edit_text(
                **msg
            )
        else:
            print("kek")

    async def send_news(self, callback_query: types.CallbackQuery | int):
        if type(callback_query) is int:
            user_id = callback_query
        else:
            try:
                await callback_query.answer()
            except aiogram.utils.exceptions.InvalidQueryID:
                pass
            user_id = callback_query.from_user.id
        user = self.database.get_user(user_id)
        emotions = json.loads(user.emotions)
        themes = json.loads(user.themes)

        if not len(self.user_news[user_id]) == 0:
            # while len(self.user_news[user_id]) != 0 and len(self.user_news[user_id][0]) != 0:
            #     self.user_news[user_id].pop(0)
            emotion, theme = self.models.predict(self.user_news[user_id][0])
            print(f"predict results: {self.user_news[user_id][0][:15]}, {emotion}, {theme}")
            while emotion not in emotions or theme not in themes:
                print(f"emo: {emotion in emotions}, the: {theme in themes}")
                self.user_news[user_id].pop(0)
                # while len(self.user_news[user_id]) != 0 and len(self.user_news[user_id][0]) != 0:
                #     self.user_news[user_id].pop(0)
                if len(self.user_news[user_id]) == 0:
                    break
                emotion, theme = self.models.predict(self.user_news[user_id][0])
                print(f"predict results: {self.user_news[user_id][0][:15]}, {emotion}, {theme}")
            if len(self.user_news[user_id]) != 0:
                print("!!!!!!!!!!!!!!!!!!!!!!")
                print(f"found: {self.user_news[user_id][0][:15]}, {emotion}, {theme}")
                print("!!!!!!!!!!!!!!!!!!!!!!")
        if len(self.user_news[user_id]) == 0:
            await self.bot.send_sticker(
                user_id,
                sticker=stickers.sad
            )
            await self.bot.send_message(
                user_id,
                text="Новости закончились!"
            )
        else:
            try:
                await self.bot.send_message(
                    user_id,
                    **messages.Message(
                        text=f"{emotion}, {theme}\n{self.user_news[user_id][0]}",
                        markup_info=[
                            ("Следующая новость", "news")
                        ],
                        parse_mode="Markdown"
                    )
                )
            except aiogram.utils.exceptions.CantParseEntities:
                await self.bot.send_message(
                    user_id,
                    **messages.Message(
                        text=f"{emotion}, {theme}\n{self.user_news[user_id][0]}",
                        markup_info=[
                            ("Следующая новость", "news")
                        ],
                        parse_mode="HTML"
                    )
                )
            self.user_news[user_id].pop(0)


if __name__ == "__main__":
    AistBot()

# import datetime
# _ = {
#     '_': 'Message',
#     'id': 93298,
#     'peer_id': {
#         '_': 'PeerChannel',
#         'channel_id': 1068197708
#     },
#     'date': datetime.datetime(2023, 7, 26, 15, 30, 15, tzinfo=datetime.timezone.utc),
#     'message': '',
#     'out': False,
#     'mentioned': False,
#     'media_unread': False,
#     'silent': False,
#     'post': True,
#     'from_scheduled': False,
#     'legacy': False,
#     'edit_hide': True,
#     'pinned': False,
#     'noforwards': False,
#     'from_id': None,
#     'fwd_from': None,
#     'via_bot_id': None,
#     'reply_to': None,
#     'media': {
#         '_': 'MessageMediaPhoto',
#         'spoiler': False,
#         'photo': {
#             '_': 'Photo',
#             'id': 5912194595624694138,
#             'access_hash': -6557128419042960771,
#             'file_reference': b'\x02?\xabgL\x00\x01lrd\xc1M\x94p\xbc\x1ed\xf8\x89\xd1\xdd\x00\xc0H\xa1zF\xa9\x91',
#             'date': datetime.datetime(2023, 7, 26, 15, 30, 10, tzinfo=datetime.timezone.utc),
#             'sizes': [
#                 {
#                     '_': 'PhotoStrippedSize',
#                     'type': 'i',
#                     'bytes': b'\x01(\x19s\xceVB\xb9\xf9sK\x14\xe7$\x97\x18\x1dFj\xb4W1J\xc0:a\x8bc9\xc8\xabM\x02\xa3\xa6\xd0\x08<\xf7\xac\xf9S\xd1\x8e\xed \x8fqFi]\xfd@\xcd?\xce\xa60*v\xc89#\x18\x14\xcd\x8f\xff\x00<\x8di*qfJm\x11Y\xda\xc2a\xcc\xe9\xb5\x81\xcf\'\x1czb\xacG"\x89\x181\xda\xeaq\x8c\xf4\xa9\xa7\x05\x9a3\x1a\xab\x15\xc1\xc5\x0f\x11\x1b\x89\xc6_\xaf\x1dk4\xf9\x8dn\x91!\x11\xc8\xbb\x8e1\xdc\x9e\xf4\x9b\xad?\xbe\x9f\x9dF\xf6\xbb\x99\x9d\xd3 \x8e\x99\xe9\xefU\xfe\xc3\x07\xf7\x9a\xa9\xc3\xcc\x9edXrJ\xecW1\x1c\x90N\xdc\x92)aEL0\xdcy\xe4\x9e\xa7\xde\x8a*"\xeda\xb7\xa3E\xb6\x95\x15rXb\xa8y\xf1\xd1Et$e&\x7f'
#                 },
#                 {
#                     '_': 'PhotoSize',
#                     'type': 'm',
#                     'w': 204,
#                     'h': 320,
#                     'size': 35361
#                 },
#                 {
#                     '_': 'PhotoSize',
#                     'type': 'x',
#                     'w': 509,
#                     'h': 800,
#                     'size': 163936
#                 },
#                 {
#                     '_': 'PhotoSizeProgressive',
#                     'type': 'y',
#                     'w': 764,
#                     'h': 1200,
#                     'sizes': [18357, 61052, 131987, 189247, 246346]
#                 }
#             ],
#             'dc_id': 4,
#             'has_stickers': False,
#             'video_sizes': []
#         },
#         'ttl_seconds': None
#     },
#     'reply_markup': None,
#     'entities': [],
#     'views': 873,
#     'forwards': 3,
#     'replies': None,
#     'edit_date': datetime.datetime(2023, 7, 26, 15, 30, 18, tzinfo=datetime.timezone.utc),
#     'post_author': None,
#     'grouped_id': 13523083320336882,
#     'reactions': None,
#     'restriction_reason': [],
#     'ttl_period': None
# }

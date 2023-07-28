from aiogram import types
from collections.abc import Mapping


class Message(Mapping):
    text: str
    markup: types.InlineKeyboardMarkup | None
    parse_mode: str
    markup_info: list[tuple]

    def __init__(
            self,
            text: str = "",
            markup_info: list[tuple] = (),
            parse_mode: str = "HTML"
    ):
        self.text = text
        self.markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    button_info[0],
                    callback_data=button_info[1]
                )
            ]
            for button_info in markup_info
        ])
        self.parse_mode = parse_mode
        self.markup_info = markup_info

    def to_dict(self):
        return {
            'text': self.text,
            'reply_markup': self.markup,
            'parse_mode': self.parse_mode
        }

    def __getitem__(self, item):
        return self.to_dict()[item]

    def __iter__(self):
        return iter(self.to_dict())

    def __len__(self):
        return len(self.to_dict())

    def copy(self):
        return Message(self.text, self.markup_info)


start = Message(
    text="<b>AIST NEWS готов к работе!</b> ✉️\n\n"
    "Выбери из каких ресурсов, ты хочешь получать новости?\n\n"
    "<b>/help</b> → У тебя возникли некоторые вопросы? Не переживай! Отправляй команду и получай подробную "
    "информацию о боте🧡",
    markup_info=[
        ("Telegram каналы", "telegram_channel_news"),
        ("Новостные сайты", "website_news")
    ]
)

ask_for_channel = Message(
    text="Напиши название или ссылку канала, который хочешь добавить, либо нажми кнопку для перехода к выбору эмоций.\n"
         "Либо напиши ссылку уже добавленного канала, чтобы убрать его",
    markup_info=[
        ("К выбору эмоций", "to_emotions")
    ]
)

channel_added = Message(
    text="Канал добавлен!"
)

channel_confirmation = Message(
    text="Это нужный канал?",
    markup_info=[
        ("Да", "confirm/yes"),
        ("Нет", "confirm/no")
    ]
)

channel_not_found = Message(
    text="Канал не найден"
)

confirmation_no = Message(
    text="Канал не был добавлен"
)

start_new = Message(
    text="Добро пожаловать в <b>AIST NEWS</b>!\n\n"
    "<b>/help</b> → У тебя возникли некоторые вопросы? Не переживай! Отправляй команду и получай подробную "
    "информацию о боте🧡",
    markup_info=[
        ("Telegram каналы", "telegram_channel_news"),
        ("Новостные сайты", "website_news")
    ]
)

choose_websites = Message(
    text="Нажми на ресурс, который хочешь добавить/убрать:",
    markup_info=[
        ("К выбору эмоций", "to_emotions")
    ]
)

choose_emotions = Message(
    text="Нажми на эмоцию, которую хочешь добавить/убрать:",
    markup_info=[
        ("К выбору тем", "to_themes")
    ]
)

choose_themes = Message(
    text="Нажми на тему, которую хочешь добавить/убрать:",
    markup_info=[
        ("К новостям", "to_news")
    ]
)

channel_removed = Message(
    text="Указанный канал был удален"
)

processing_news = Message(
    text="Новости обрабатываются..."
)

help = Message(
    text="<b>Подрбоная информация</b> 🤖️\n\n" + \
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
        "Узнал все, что хотел? Тогда пиши в чат → <b>/start</b> и узнавай что то новенькое🧡",
    parse_mode="HTML"
)

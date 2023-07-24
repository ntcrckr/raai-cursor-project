from telethon.tl.custom import Button


class MyButton:
    button_telegram_chanel_news = Button.inline(
        "Telegram каналы",
        data="button_telegram_chanel_news"
    )
    button_website_news = Button.inline(
        "Новостные сайты",
        data="button_website_news"
    )
    start_buttons = [
        button_telegram_chanel_news,
        button_website_news
    ]

    button_news_change = Button.inline(
        "Закончить выбор",
        data="button_news_change"
    )
    news_change_buttons = [
        button_news_change
    ]
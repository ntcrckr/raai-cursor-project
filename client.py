from telethon import TelegramClient, functions, types
import config


async def get_channel_by_name(channel_name: str) -> types.Channel:
    result: types.contacts.Found = await client(functions.contacts.SearchRequest(
        q=channel_name,
        limit=100
    ))
    return result.chats[0]


async def get_channel_by_link(channel_link: str) -> types.Channel:
    result = await client.get_entity(channel_link)
    return result


async def get_channel_messages(channel: types.Channel):
    async for post in client.iter_messages(channel):
        print(post.sender_id, ':', post.text)


async def main():
    channel = await get_channel_by_name("testchannelproject")
    # channel = await get_channel_by_link("https://t.me/true_figma")
    # print(channel)
    await get_channel_messages(channel)


if __name__ == "__main__":
    client: TelegramClient
    with TelegramClient(
            'anon',
            config.api_id,
            config.api_hash,
            **config.my_credentials
    ) as client:
        client.loop.run_until_complete(main())

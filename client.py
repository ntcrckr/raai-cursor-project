from telethon import TelegramClient, functions, types
import config
import telethon


class Client:
    client: TelegramClient

    def __init__(self):
        self.client = TelegramClient(
            'anon',
            config.api_id,
            config.api_hash,
            **config.my_credentials
        )
        self.client.start()

    async def get_channel_by_name(self, channel_name: str) -> types.Channel:
        result: types.contacts.Found = await self.client(
            functions.contacts.SearchRequest(
                q=channel_name,
                limit=100
            )
        )
        return result.chats[0]

    async def get_channel_by_link(self, channel_link: str) -> types.Channel:
        result = await self.client.get_entity(channel_link)
        return result

    async def get_channel_messages(self, channel_id: int):
        channel = await self.client.get_entity(channel_id)
        # self.client.get_channel_messages()
        return (
            post.text
            # if post.text
            # else print(post.__dict__)
            async for post
            in self.client.iter_messages(channel, limit=20)
        )
# from telethon.tl import patched
# patched.Message().__dict__

if __name__ == "__main__":
    # client: TelegramClient
    # with TelegramClient(
    #         'anon',
    #         config.api_id,
    #         config.api_hash,
    #         **config.my_credentials
    # ) as client:
    #     client.loop.run_until_complete(main())
    pass

import sqlalchemy as db
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from enum import Enum


Base = declarative_base()


class Emotion(str, Enum):
    """
    Enum for emotions
    """
    positive = "pos"
    neutral = "neu"
    negative = "neg"


class Theme(str, Enum):
    """
    Enum for themes
    """
    russia = "rus"
    world = "wor"
    sport = "spo"
    economics = "eco"
    former_ussr = "uss"
    security_forces = "for"
    internet_and_mass_media = "ima"
    science_and_technology = "sat"
    culture = "cul"
    from_life = "lif"
    travel = "tra"
    values = "val"
    home = "hom"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    emotions = Column(String)
    themes = Column(String)

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.id}, {self.emotions}, {self.themes}"


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True)
    link = Column(String)

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.id}, {self.link}"


class UserToChannel(Base):
    __tablename__ = "user_to_channel"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))
    user = relationship("User")
    channel = relationship("Channel")

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.id}, {self.user_id}, {self.channel_id}"


class Database:
    engine: db.Engine
    session: db.orm.Session

    def __init__(self, path: str = "aist.sqlite"):
        self.engine = db.create_engine(f"sqlite:///{path}")
        self.session = db.orm.sessionmaker(bind=self.engine)()

    def __new_user(
            self,
            user_id: User.id = None,
            emotions: User.emotions = None,
            themes: User.themes = None,
            user: User = None
    ):
        if user is not None:
            self.session.add(user)
        else:
            self.session.add(User(
                id=user_id,
                emotions=emotions,
                themes=themes
            ))
        self.session.commit()

    def __new_channel(
            self,
            channel_id: Channel.id = None,
            link: Channel.link = None,
            channel: Channel = None
    ):
        if channel is not None:
            self.session.add(channel)
        else:
            self.session.add(Channel(
                id=channel_id,
                link=link
            ))
        self.session.commit()

    def __new_user_to_channel(
            self,
            user_id: User.id,
            channel_id: Channel.id,
    ):
        self.session.add(UserToChannel(
            user_id=user_id,
            channel_id=channel_id
        ))
        self.session.commit()

    def __check_user(
            self,
            user_id: User.id
    ) -> bool:
        _result = self.session.execute(
            db.select(User).where(User.id == user_id)
        )
        return len(_result.scalars().all()) != 0

    def __check_channel(
            self,
            channel_id: Channel.id
    ) -> bool:
        _result = self.session.execute(
            db.select(Channel).where(Channel.id == channel_id)
        )
        return len(_result.scalars().all()) != 0

    def __get_user(
            self,
            user_id: User.id
    ) -> User:
        _result = self.session.execute(
            db.select(User).where(User.id == user_id)
        )
        return _result.scalar_one()

    def __get_channel(
            self,
            channel_id: Channel.id
    ) -> User:
        _result = self.session.execute(
            db.select(Channel).where(Channel.id == channel_id)
        )
        return _result.scalar_one()

    def __update_user(
            self,
            user_id: User.id = None,
            emotions: User.emotions = None,
            themes: User.themes = None,
            user: User = None
    ):
        if user is not None:
            pass

    def register_user(
            self,
            user_id: User.id
    ) -> bool:
        """
        Creates user if not existent (with empty emotions and themes)
        :param user_id: Telegram id of User
        :return: True if user exists, False if created new one
        """
        if not self.__check_user(user_id):
            _user = User(id=user_id, emotions="", themes="")
            self.__new_user(user=_user)
            return False
        return True

    def add_channel_to_user(
            self,
            user_id: User.id,
            channel_id: Channel.id,
            link: Channel.link
    ):
        """
        Adds user_to_channel connection and created new Channel if not existent
        :param user_id: Telegram id of User
        :param channel_id: Telegram id of Channel
        :param link: Telegram link of Channel TODO in what form?
        :return: True if channel existed, False if created new channel
        """
        if not self.__check_channel(channel_id):
            _channel = Channel(id=channel_id, link=link)
            self.__new_channel(_channel)
            self.__new_user_to_channel(user_id, channel_id)
            return False
        self.__new_user_to_channel(user_id, channel_id)
        return True

    def update_user_preferences(
            self,
            user_id: User.id,
            emotions: list[Emotion] = None,
            themes: list[Theme] = None
    ):
        str_emotions = json.dumps(emotions)
        str_themes = json.dumps(themes)
        # self.


if __name__ == '__main__':
    # database = Database()
    # print(database.register_user(123))
    import json
    print(json.dumps([Emotion.neutral, Emotion.positive]))
    pass

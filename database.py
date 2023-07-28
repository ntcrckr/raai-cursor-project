import sqlite3
from typing import List

import sqlalchemy as db
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.exc import IntegrityError
from enum import Enum
import json


Base = declarative_base()


class Emotion(str, Enum):
    """
    Enum for emotions
    """
    positive = "Позитивный"
    neutral = "Нейтральный"
    negative = "Негативный"


class Theme(str, Enum):
    """
    Enum for themes
    """
    russia = "Россия"
    world = "Мир"
    sport = "Спорт"
    economics = "Экономика"
    former_ussr = "Бывший СССР"
    security_forces = "Силовые структуры"
    internet_and_mass_media = "Интернет и СМИ"
    science_and_technology = "Наука и техника"
    culture = "Культура"
    from_life = "Из жизни"
    travel = "Путешествия"
    values = "Ценности"
    home = "Дом"


all_themes = (
    Theme.russia,
    Theme.world,
    Theme.sport,
    Theme.economics,
    Theme.former_ussr,
    Theme.security_forces,
    Theme.internet_and_mass_media,
    Theme.science_and_technology,
    Theme.culture,
    Theme.from_life,
    Theme.travel,
    Theme.values,
    Theme.home
)


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

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), primary_key=True)
    user = relationship("User", foreign_keys="UserToChannel.user_id")
    channel = relationship("Channel", foreign_keys="UserToChannel.channel_id")

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.user_id}, {self.channel_id}"


class UserToWebsite(Base):
    __tablename__ = "user_to_website"

    id = Column(Integer, primary_key=True)
    tv1 = Column(Boolean)
    fon = Column(Boolean)
    rug = Column(Boolean)

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.id}, {self.tv1}, {self.fon}, {self.rug}"


class Database:
    engine: db.Engine
    session: db.orm.Session

    def __init__(self, path: str = "aist.sqlite"):
        self.engine = db.create_engine(f"sqlite:///{path}")
        self.session = db.orm.sessionmaker(bind=self.engine)()

    def __new_user(
            self,
            user_id: User.id = None,
            emotions: User.emotions = "[]",
            themes: User.themes = "[]",
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
    ) -> bool:
        """
        Adds line to user_to_channel table
        :param user_id: Telegram id of User
        :param channel_id: Telegram id of Channel
        :return: True if connection already existed, False if new connection
        """
        try:
            self.session.add(UserToChannel(
                user_id=user_id,
                channel_id=channel_id
            ))
            self.session.commit()
            return False
        except IntegrityError:
            self.session.rollback()
            # print(f"user_to_channel({user_id}, {channel_id}) already exists")
            return True

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

    def __check_user_to_channel(
            self,
            user_id: User.id,
            channel_id: Channel.id
    ):
        pass

    def get_user(
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
            _user_id = user.id
        else:
            _user_id = user_id
        _user: User = self.session.execute(
            db.select(User).filter_by(id=user_id)
        ).scalar_one()
        _user.emotions = emotions
        _user.themes = themes
        self.session.commit()

    def register_user(
            self,
            user_id: User.id
    ) -> bool:
        """
        Creates user if not existent (with empty emotions and themes)
        :param user_id: Telegram id of User
        :return: True if user exists, False if created new one
        """
        try:
            self.session.add(
                UserToWebsite(
                    id=user_id,
                    tv1=True,
                    fon=True,
                    rug=True
                )
            )
            self.session.commit()
        except db.exc.IntegrityError:
            self.session.rollback()
        if not self.__check_user(user_id):
            _user = User(id=user_id, emotions="[]", themes="[]")
            self.__new_user(user=_user)
            return False
        return True

    def delete_user_to_channel(
            self,
            user_id: User.id,
            channel_id: Channel.id
    ):
        self.session.execute(
            db.delete(UserToChannel).where(
                db.and_(
                    UserToChannel.user_id == user_id,
                    UserToChannel.channel_id == channel_id
                )
            )
        )
        self.session.commit()

    def add_channel_to_user(
            self,
            user_id: User.id,
            channel_id: Channel.id,
            link: Channel.link
    ) -> bool:
        """
        Adds user_to_channel connection and created new Channel if not existent
        :param user_id: Telegram id of User
        :param channel_id: Telegram id of Channel
        :param link: Telegram link of Channel TODO in what form?
        :return: True if connection to channel existed, False if created new one
        """
        # print(user_id, channel_id, link)
        if not self.__check_channel(channel_id):
            _channel = Channel(id=channel_id, link=link)
            self.__new_channel(channel=_channel)
        existed = self.__new_user_to_channel(user_id, channel_id)
        return existed

    def get_channels_by_user(self, user_id: User.id) -> List[Channel]:
        result = self.session.execute(
            db.select(Channel)
            .join(UserToChannel)
            .filter(UserToChannel.user_id == user_id)
        ).fetchall()
        return [row[0] for row in result]

    def update_user_preferences(
            self,
            user_id: User.id,
            emotions: list[Emotion] = None,
            themes: list[Theme] = None
    ):
        str_emotions = json.dumps(emotions)
        str_themes = json.dumps(themes)
        # self.

    def get_websites_by_user(self, user_id: User.id) -> UserToWebsite:
        return self.session.execute(
            db.select(UserToWebsite).where(UserToWebsite.id == user_id)
        ).scalar_one()

    def update_websites_by_user(
            self,
            user_id: UserToWebsite.id,
            tv1: UserToWebsite.tv1,
            fon: UserToWebsite.fon,
            rug: UserToWebsite.rug
    ):
        user_to_website: UserToWebsite = self.session.execute(
            db.select(UserToWebsite).filter_by(id=user_id)
        ).scalar_one()
        user_to_website.tv1 = tv1
        user_to_website.fon = fon
        user_to_website.rug = rug
        self.session.commit()


if __name__ == '__main__':
    # database = Database()
    # Base.metadata.create_all(database.engine)
    # print(database.get_websites_by_user("326271189"))
    # print(database.get_channels_by_user("326271189"))
    # l_e = []
    # j_l_e = json.dumps(l_e)
    # e = json.loads(j_l_e)
    # print(j_l_e)
    # print(e)
    # print(Emotion.positive in e, Emotion.neutral in e, Emotion.negative in e)
    # print(Theme("rus"))
    database = Database()
    # result = database.session.execute(
    #     db.select(User)
    # ).fetchall()
    # for res in result:
    #     database.session.execute(
    #         db.delete(User).where(User.id == res[0].id)
    #     )
    # database.session.commit()
    result = database.session.execute(
        db.select(UserToWebsite)
    ).fetchall()
    for res in result:
        print(res)
    pass

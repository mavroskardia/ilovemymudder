import bcrypt

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy import create_engine

from ..common import config

Base = declarative_base()

class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(4000), nullable=False)
    commands_file = Column(String(255))

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    pwhash = Column(String(255), nullable=False)

    strength = Column(Integer, default=1)
    dexterity = Column(Integer, default=1)
    intelligence = Column(Integer, default=1)
    health = Column(Integer, default=1)

    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)

    current_room_id = Column(Integer, ForeignKey('rooms.id'))
    current_room = relationship(Room, backref=backref('users', order_by=id))


def get_storage_session():
    engine = create_engine(config.database)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    return session

def store_user(username, salt, passwd_hash):
    new_user = User(name=username, salt=salt, pwhash=passwd_hash)
    session = get_storage_session()
    session.add(new_user)
    session.commit()

def is_user_match(username, passwd):
    session = get_storage_session()
    user = session.query(User).filter(User.name == username).first()
    if not user:
        return False

    passwd_hash = bcrypt.hashpw(passwd.encode(), user.salt)

    return passwd_hash == user.pwhash

def get_user(username):
    session = get_storage_session()
    user = session.query(User).filter(User.name == username).first()

    if not user:
        return None

    return user


if __name__ == '__main__':
    print('running sqlalchemy tests')

    session = get_storage_session()

    new_user = User(name='chryso', salt='hi', pwhash='there')
    session.add(new_user)
    session.commit()

import pdb
import bcrypt

from sqlalchemy import Table, Column, ForeignKey, Integer, String, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from ..common import config

Base = declarative_base()


class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True)
    is_start = Column(Boolean)
    module = Column(String(255))


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    pwhash = Column(String(255), nullable=False)

    strength = Column(Integer, default=1)
    dexterity = Column(Integer, default=1)
    intelligence = Column(Integer, default=1)
    health = Column(Integer, default=10)

    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)

    current_room_id = Column(Integer, ForeignKey('rooms.id'))
    current_room = relationship(Room, backref=backref('users', order_by=id))

    status = Column(Integer, default=0) # bitmask of all possible statuses    


def get_session():
    engine = create_engine(config.database)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    return session

def store_user(username, salt, passwd_hash):
    new_user = User(name=username, salt=salt, pwhash=passwd_hash)
    session = get_session()
    start = None
    try:
        start = session.query(Room).filter(Room.is_start).one()
        new_user.current_room = start
        session.add(new_user)
        session.commit()
        return True
    except NoResultFound as e:
        print('Unable to find a starting room to assign to user. Please run the "makerooms" server command first.')

    return False

def is_user_match(username, passwd, session=None):
    session = session or get_session()
    user = session.query(User).filter(User.name == username).first()
    if not user:
        return False

    passwd_hash = bcrypt.hashpw(passwd.encode(), user.salt)

    return passwd_hash == user.pwhash

def get_user(username, session=None):
    session = session or get_session()
    user = session.query(User).filter(User.name == username).first()

    if not user:
        return None

    return user, session

def get_starting_room(session=None):
    session = session or get_session()
    return session.query(Room).filter(Room.is_start).one()

def update_user_room(user, room_module, session=None):
    session = session or get_session()
    room = session.query(Room).filter(Room.module == room_module).first()
    user.current_room = room
    session.commit()
    return room, session

def store_room_from_module(module, session=None):
    session = session or get_session()
    room = session.query(Room).filter(Room.module == module.__name__).first()
    if not room:
        print('Creating new room for {}'.format(module.__name__))
        room = Room(is_start=False, module=module.__name__)
        session.commit()
    return room, session

if __name__ == '__main__':
    print('running sqlalchemy tests')

    session = get_session()

    new_user = User(name='chryso', salt='hi', pwhash='there')
    session.add(new_user)
    session.commit()

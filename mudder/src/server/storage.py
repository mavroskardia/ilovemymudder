import bcrypt

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from ..common import config

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    pwhash = Column(String(255), nullable=False)


class UserState(Base):
    __tablename__ = 'userstate'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)


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


if __name__ == '__main__':
    print('running sqlalchemy tests')

    session = get_storage_session()

    new_user = User(name='chryso', salt='hi', pwhash='there')
    session.add(new_user)
    session.commit()

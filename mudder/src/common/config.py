import os

host = 'localhost'
port = 55120
buffer_size = 1024
version = '001'
database_file = 'game.db'
database = 'sqlite:///' + database_file
storydir = os.path.join('src', 'story')

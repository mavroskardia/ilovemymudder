import time
import asyncio
import getpass
import threading

from enum import Enum

try:
    from socket import socketpair
except ImportError:
    from asyncio.windows_utils import socketpair

from ..common import config
from .state import GameState


class ClientState(Enum):
    Initial = 1
    Handshake = 2
    Authentication = 3
    Command = 4


class ClientProtocol(asyncio.Protocol):

    def __init__(self, client, username, passwd, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username
        self.passwd = passwd  # should probably send over SSL if I keep going
        self.client = client
        self.state = ClientState.Initial

        self.client_actions = {
            ClientState.Handshake: self.receive_handshake,
            ClientState.Authentication: self.receive_auth,
            ClientState.Command: self.receive_command_result,
        }

        self.interpreter = Interpreter(self)

    def connection_made(self, transport):
        self.transport = transport
        self.send_handshake()

    def data_received(self, data):
        result = self.client_actions.get(self.state, self.unimplemented_action)(data)

    def connection_lost(self, exc):
        print('connection lost')
        self.interpreter_done = True
        self.interpreter.stop()
        self.client.loop.stop()

    def send_handshake(self):
        self.transport.write(config.version.encode())
        self.state = ClientState.Handshake

    def receive_handshake(self, data):
        msg = data.decode().strip()
        if msg != config.version:
            print('Invalid handshake, quitting...')
            self.transport.close()

        s = '{}:{}'.format(self.username, self.passwd)
        self.transport.write(s.encode())
        self.state = ClientState.Authentication

    def receive_auth(self, data):
        msg = data.decode().strip()
        if msg == 'NO':
            print('Failed to authenticate, quitting...')
            self.transport.close()
        elif msg == 'OK':
            print('\n\tLogged in successfully! Loading game...')
            self.state = ClientState.Command
            self.interpreter.start()

    def receive_command_result(self, data):
        msg = data.decode().strip()
        if msg.startswith('GS'):
            self.interpreter.set_game_state(msg[2:])
        else:
            print(msg)

    def unimplemented_action(self, data):
        print('client tried to execute an unimplemented state "{}"'.format(self.state))


class Interpreter(object):

    def __init__(self, client_protocol):
        self.protocol = client_protocol
        self.commands = {
            'echo': lambda *args: self.send('echo ' + (' '.join(args))),
            'serverquit': lambda: self.send('quit'),
            'quit': lambda: self.send('disconnect'),
            'say': self.say,
            'help': self.help,
            'stats': lambda: self.send('stats'),
            'look': lambda: self.send('look'),
        }

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self, *args):
        print('stopping interpreter and closing transport')
        self.running = False
        self.protocol.transport.close()

    def send(self, msg):
        self.protocol.transport.write(msg.encode())

    def run(self):
        while self.running:
            cmd = input('\t=> ')
            if not cmd:
                continue
            cmd, *args = [c.strip() for c in cmd.split(' ') if c]
            self.commands.get(cmd, lambda: self.help('{} is not valid. These are your commands:'.format(cmd)))(*args)


    def say(self, *args):
        msg = 'say ' + ' '.join(args)
        self.send(msg)

    def help(self, msg=None, *args):
        commands = '\n\t\t' + '\n\t\t'.join(self.commands.keys())
        if msg:
            print('\t'+msg)
        print(commands)
        print('\n\t\tThere may also be area-specific commands that you can find!\n')

class Client(object):

    def run(self):
        print('''
      _____     __                                                ___    _
      \_   \   / /  _____   _____    /\/\  _   _    /\/\  /\ /\  /   \__| | ___ _ __
       / /\/  / /  / _ \ \ / / _ \  /    \| | | |  /    \/ / \ \/ /\ / _` |/ _ \ '__|
    /\/ /_   / /__| (_) \ V /  __/ / /\/\ \ |_| | / /\/\ \ \_/ / /_// (_| |  __/ |
    \____/   \____/\___/ \_/ \___| \/    \/\__, | \/    \/\___/___,' \__,_|\___|_|
                                           |___/

    Welcome! Please enter your username and password to begin.

    (If you haven't created a username and password yet, use the
    server command "createuser")
''')

        self.main_loop(*self.get_userinfo())

    def get_userinfo(self):
        return input('\tusername > '), getpass.getpass('\tpassword > ')

    def main_loop(self, username, passwd):
        self.loop = asyncio.get_event_loop()

        coro = self.loop.create_connection(lambda: ClientProtocol(self, username, passwd), config.host, config.port)

        self.loop.run_until_complete(coro)
        self.loop.run_forever()
        self.loop.close()

import time
import asyncio

from ..common import config


class Client(object):

    @asyncio.coroutine
    def send(self, message, loop):
        reader, writer = yield from asyncio.open_connection(config.host, config.port, loop=loop)

        while True:
            try:
                print('Send: %r' % message)
                writer.write(message.encode())

                data = yield from reader.read(config.buffer_size)
                print('Received: %r' % data.decode())

                time.sleep(5)
            except KeyboardInterrupt:
                pass

        print('Closing socket')
        writer.close()


    def run(self):

        message = 'hallo'
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.send(message, loop))
        loop.close()

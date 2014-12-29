import asyncio

from ..common import config


class Server(object):

    @asyncio.coroutine
    def handle(self, reader, writer):
        data = yield from reader.read(config.buffer_size)
        message = data.decode()
        addr = writer.get_extra_info('peername')
        print('received %r from %r' % (message, addr))

        print('Send: %r' % message.upper())
        writer.write(message.upper().encode())
        yield from writer.drain()

        print('all done')
        writer.close()


    def run(self):
        loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.handle, config.host, config.port, loop=loop)
        server = loop.run_until_complete(coro)

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print('caught Ctrl-C')

        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

import asyncio
import logging

from utils import MetaSingleton
from commands import Command
from settings import app_config

logger = logging.getLogger(app_config.LOGGER_NAME)


class Server(metaclass=MetaSingleton):
    TIMEOUT: float = 2.5
    BUFFER: int = 1024

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.clients = {}

    async def disconnect_client(self, addr: tuple):
        if addr in self.clients:
            _, writer = self.clients.pop(addr)
            writer.close()
            await writer.wait_closed()
            logger.info(f'Client {addr} disconnected and removed')
        else:
            logger.error(f'Client {addr} not found')

    async def read_response(self, addr: tuple):
        response = b''
        reader, _ = self.clients[addr]
        while True:
            try:
                print(self.clients.keys())
                answer = await asyncio.wait_for(reader.read(self.BUFFER), self.TIMEOUT)
                if not answer:
                    logger.debug(f'answer b"", client {addr} close connect')
                    break
                response += answer
            except TimeoutError:
                logger.debug(f'Execution timeout -> get {response}')
                break
        if response:
            return response
        await self.disconnect_client(addr)

    async def send_command(self, addr: tuple, command: Command):
        _, writer = self.clients[addr]
        try:
            writer.write(command.COMMAND.encode() + b'\n')
            await writer.drain()
        except (ConnectionResetError, BrokenPipeError) as e:
            logger.error(f'Connection close {addr}: {e}')
            await self.disconnect_client(addr)

    async def request(self, addr: tuple, command: Command):
        if addr in self.clients:
            await self.send_command(addr, command)
            return await self.read_response(addr)

    async def handler(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        logger.info(f'client {addr} connect')

        if addr not in self.clients:
            self.clients[addr] = (reader, writer)

    async def start(self):
        server = await asyncio.start_server(self.handler, self.host, self.port)
        logger.info(f'Server start {self.host}:{self.port}')
        async with server:
            await server.serve_forever()

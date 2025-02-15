import asyncio
import logging

from settings import env_config, app_config
from server import Server
from commands import ScreenshotCommand

app_config.configure_logging()
logger = logging.getLogger(app_config.LOGGER_NAME)


async def main():
    server = Server(env_config.HOST, env_config.PORT)
    asyncio.create_task(server.start())
    while True:
        if server.clients:
            client = next(iter(server.clients.keys()))
            await server.request(client, ScreenshotCommand)
        await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())

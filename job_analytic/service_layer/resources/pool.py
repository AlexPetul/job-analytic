from aiohttp import ClientSession, DummyCookieJar, TCPConnector

from .singleton import Singleton


class ResourcePool(metaclass=Singleton):
    def __init__(self):
        self._http_session = ClientSession(connector=TCPConnector(limit=200), cookie_jar=DummyCookieJar())

    @property
    async def http_session(self):
        return await self._http_session.__aenter__()

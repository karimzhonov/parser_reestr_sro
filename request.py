import asyncio
from utils import get_headers
from fake_useragent import UserAgent
from aiohttp import ClientSession, ClientConnectionError


async def get(url, **kwargs):
    try:
        async with ClientSession(trust_env=True) as session:
            response = await session.get(url, headers=get_headers(), **kwargs)
            return await response.text()
    except ClientConnectionError:
        await asyncio.sleep(3)
        return await get(url, **kwargs)


async def post(url, headers=get_headers(), json=None, **kwargs):
    try:
        ua = UserAgent()
        headers["user-agent"] = ua.random
        async with ClientSession() as session:
            response = await session.post(url, headers=headers, json=json, **kwargs)
            return await response.text()
    except ClientConnectionError:
        await asyncio.sleep(3)
        return await post(url, headers, json, **kwargs)

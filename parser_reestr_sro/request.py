import asyncio
from fake_useragent import UserAgent
from logger import logger
from aiohttp import ClientSession, ClientError, TCPConnector


def get_headers():
    ua = UserAgent()
    return {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": ua.random,
    }


async def get(url, headers=None, json=None, **kwargs):
    if headers is None:
        headers = get_headers()
    try:
        async with ClientSession(trust_env=True, connector=TCPConnector(verify_ssl=False)) as session:
            response = await session.get(url, headers=headers, json=json, **kwargs)
            return await response.text()
    except ClientError as _exp:
        await asyncio.sleep(3)
        logger.error(_exp)
        return await get(url, **kwargs)


async def post(url, headers=None, json=None, **kwargs):
    if headers is None:
        headers = get_headers()
    try:
        ua = UserAgent()
        headers["user-agent"] = ua.random
        async with ClientSession(trust_env=True, connector=TCPConnector(verify_ssl=False)) as session:
            response = await session.post(url, headers=headers, json=json, **kwargs)
            return await response.text()
    except ClientError:
        await asyncio.sleep(3)
        logger.error(_exp)
        return await post(url, headers, json, **kwargs)

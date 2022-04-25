import json
import asyncio
from excel import Excel
from request import post
from logger import logger
from datetime import datetime

DATA = []
PAGE_COUNT = 1
URL = "https://reestr.nopriz.ru"
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/json",
    "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"100\", \"Google Chrome\";v=\"100\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
}


async def _sort_card_data(data):
    """
    Keywords to sort
    ------------------------------------------------------
    'Полное наименование': Any string
    'ИНН': Any string of numbers
    'Номер контактного телефона': Any string of numbers
    'Адрес': Any string of numbers
    'ФИО': String
    'Статус члена': bool
    ------------------------------------------------------
    'Сведения о наличии права': bool
    ------------------------------------------------------
    'Размер взноса в компенсационный фонд возмещения вреда': bool, True if value > 0.00
    'Размер взноса в компенсационный фонд обеспечения договорных обязательств': bool, True if value > 0.00
    ------------------------------------------------------
    :param data: dict of information with this keys
    """
    labels = list(data.keys())
    labels.sort()
    data = {key: data[key] for key in labels}
    DATA.append(data)


async def get_card_data(_id):
    return_data = {}
    _url = f'{URL}/api/member/{_id}/info'
    data = await post(_url, HEADERS)
    data = json.loads(data)['data']
    return_data['Полное наименование'] = f"{data.get('full_description', '')} ({data.get('short_description', '')})"
    return_data['ИНН'] = data.get('inn', '')
    return_data['Номер контактного телефона'] = data.get('phones', '')
    return_data['Адрес'] = f"{data.get('index', '')}, {data.get('country', '')} {data.get('subject', '')}, " \
                           f"{data.get('locality', '')} {data.get('street', '')} {data.get('house', '')} " \
                           f"{data.get('room', '')}"
    return_data['ФИО'] = data.get('director', '')
    return_data['Статус члена'] = True if data['accordance_status']['code'] == '1' else False
    try:
        return_data['Сведения о наличии права'] = True if data['right']['right_status']['code'] == '1' else False
    except KeyError:
        return_data['Сведения о наличии права'] = False
    try:
        return_data['Размер взноса в компенсационный фонд возмещения вреда'] = True \
            if float(data['compensation_fund_fee_vv']) > 0 else False
    except KeyError:
        return_data['Размер взноса в компенсационный фонд возмещения вреда'] = False
    try:
        return_data['Размер взноса в компенсационный фонд обеспечения договорных обязательств'] = True \
            if float(data['compensation_fund_fee_odo']) > 0 else False
    except KeyError:
        return_data['Размер взноса в компенсационный фонд обеспечения договорных обязательств'] = False
    return return_data


async def get_page_info(page_number):
    body = {
        "filters": {},
        "page": page_number,
        "pageCount": "20",
        "sortBy": {"registry_registration_date": "DESC"}
    }
    url = f"{URL}/api/sro/all/member/list"
    response = await post(url, headers=HEADERS, json=body)
    data = json.loads(response)['data']
    return data


async def get_page_data(page_number):
    try:
        info = await get_page_info(page_number)
        for card_info in info['data']:
            _id = card_info['id']
            data = await get_card_data(_id)
            if data is not None:
                await _sort_card_data(data)
    except Exception as _exp:
        logger.error(_exp)


async def _collect_tasks(start, finish):
    tasks = []
    for p in range(start, finish + 1):
        tasks.append(asyncio.create_task(get_page_data(p)))
    await asyncio.gather(*tasks)


async def get_page_count():
    data = await get_page_info(1)
    return int(data['countPages'])


async def async_collect_data(file_path: str, chunk_save: int = None, chunk: int = None):
    """
    Collect information from URL and save to file_path
    :param file_path: Save path
    :param chunk_save: Chunk of save data
    :param chunk: Count of async requests (if big then 30 may be blocking)
    """
    try:
        if chunk_save is None: chunk_save = 10000
        if chunk is None: chunk = 25
        t0 = datetime.now()
        finish = await get_page_count()
        # Start parsing
        _start, counter = 1, 0
        for _finish in logger.range(range(1, finish + 1), desc=URL):
            counter += 1
            if counter >= chunk:
                await _collect_tasks(_start, _finish)
                _start, counter = _finish + 1, 0
            # Primejutichnaya saxraneniya
            if len(DATA) >= chunk_save:
                Excel.save(DATA, file_path)
                DATA.clear()
        if counter > 0:
            await _collect_tasks(_start, finish + 1)
        # Esli ostalis ne saxranennie to saxranit
        if len(DATA) > 0:
            Excel.save(DATA, file_path)
        logger.info(f'Parsing finished: {URL}')
        logger.info(f'Wasted time: {datetime.now() - t0}')
    except Exception as _exp:
        logger.error(_exp)


def sync_collect_data(file_path: str, chunk_save: int = None):
    if chunk_save is None: chunk_save = 10000
    t0 = datetime.now()
    asyncio.run(get_page_count())
    finish = PAGE_COUNT
    for p in logger.range(range(1, finish + 1), desc=URL):
        asyncio.run(get_page_data(p))
        if len(DATA) >= chunk_save:
            Excel.save(DATA, file_path)
            DATA.clear()
    if len(DATA) > 0:
        Excel.save(DATA, file_path)
    logger.info(f'Parsing finished: {URL}')
    logger.info(f'Wasted time: {datetime.now() - t0}')

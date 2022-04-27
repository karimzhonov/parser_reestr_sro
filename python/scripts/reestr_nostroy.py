import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from excel import Excel
from request import get
from logger import logger

from keywords import NEED_INFORMATION_KEYS, SVEDENIYA_O_NALICHI_PRAV_KEY

URL = 'https://reestr.nostroy.ru'
DATA = []
PAGE_COUNT = 1


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


async def _get_card_data(url):
    """Get information from card"""
    data = {}
    # Vkladka Сведения о члене саморегулируемой организации.
    response = await get(url)
    soup = BeautifulSoup(response, features='lxml')
    table_cols = soup.find('tbody').find_all('tr')[1:]
    for i, col in enumerate(table_cols):
        key = col.find('th').get_text(strip=True).strip(':')
        value = col.find('td').get_text(strip=True)
        if 'Идентификационный номер налогоплательщика' in key:
            data['ИНН'] = value
            continue
        if 'Фамилия' in key:
            data['ФИО'] = value
            continue
        if 'Статус члена' in key:
            data['Статус члена'] = True if value == 'Является членом' else False
            continue
        for nkey in NEED_INFORMATION_KEYS:
            if nkey in key:
                data[nkey] = value
    # Vkladka Сведения о наличии права
    response = await get(f'{url}/rights')
    soup = BeautifulSoup(response, features='lxml')
    table_body = soup.find('table', class_='table table-bordered')
    data[SVEDENIYA_O_NALICHI_PRAV_KEY] = False if table_body is None else True
    # Vkladka Сведения о Компенсационных фондах
    response = await get(f'{url}/compensation')
    soup = BeautifulSoup(response, features='lxml')
    table_rows = soup.find('div', id='block-compensation-member-content').find_all('div', class_='compensation-title')
    for row in table_rows:
        # Getting information
        row_text = row.get_text(strip=True).strip('-')
        value = row.find('u').get_text(strip=True).lower()
        key = row_text.replace(value, '').replace('составляет', '')[1:]
        # Remove words
        value = value.replace(' ', '').replace('рублей.', '').replace('рубля.', '').replace('рубль.', '')
        # Checking
        try:
            value = True if float(value) > 0 else False
        except ValueError:
            value = True
        data[key] = value
    return data


async def get_page_data(page_number):
    """Get information from page"""
    try:
        url = f'{URL}/reestr?sort=m.id&direction=asc&page={page_number}'
        response = await get(url)
        soup = BeautifulSoup(response, features='lxml')
        card_items = soup.find('tbody').find_all('tr')
        for card_item in card_items:
            rel = card_item.get('rel')
            rel = f'{URL}{rel}'
            data = await _get_card_data(rel)
            if data is not None:
                await _sort_card_data(data)
    except Exception as _exp:
        logger.error(_exp)


async def get_page_count():
    """Get pages count"""
    global PAGE_COUNT
    response = await get(f'{URL}/reestr')
    soup = BeautifulSoup(response, features='lxml')
    # Max Page number
    pagination = soup.find('ul', {'class': 'pagination'})
    pages = pagination.find_all('li')
    result = int(pages[-3].text)
    PAGE_COUNT = result
    return result


async def _collect_tasks(start, finish):
    """Collect async tasks"""
    tasks = []
    for p in range(start, finish + 1):
        tasks.append(asyncio.create_task(get_page_data(p)))
    await asyncio.gather(*tasks)


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
                Excel.save_dicts(DATA, file_path)
                DATA.clear()
        if counter > 0:
            await _collect_tasks(_start, finish + 1)
        # Esli ostalis ne saxranennie to saxranit
        if len(DATA) > 0:
            Excel.save_dicts(DATA, file_path)
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
            Excel.save_dicts(DATA, file_path)
            DATA.clear()
    if len(DATA) > 0:
        Excel.save_dicts(DATA, file_path)
    logger.info(f'Parsing finished: {URL}')
    logger.info(f'Wasted time: {datetime.now() - t0}')

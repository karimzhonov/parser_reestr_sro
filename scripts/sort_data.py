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
"""
from logger import logger
from datetime import datetime


def sort_nostroy(data: list[dict]):
    t0 = datetime.now()
    for i, card in logger.range(enumerate(data), desc='Sort nostroy'):
        if not (card['Статус члена'] and card['Сведения о наличии права']
                and card['Размер взноса в компенсационный фонд возмещения вреда']):
            del data[i]
    logger.info(f'Sorted NOSTROY information count - {len(data)}')
    logger.info(f'Wasted time: {datetime.now() - t0}')
    return data


def sort_nopriz(nostroy_data: list[dict], nopriz_data: list[dict]):
    logger.info(f'NOSTROY Information count - {len(nostroy_data)}')
    logger.info(f'NOPRIZ Information count - {len(nopriz_data)}')
    # dublikat bazi nostroy
    t0 = datetime.now()
    for ii, nopriz_card in logger.range(enumerate(nopriz_data), desc='Sort nopriz'):
        # Praverka nopriz_card yavlyaetsali chlenom
        if nopriz_card['Статус члена'] and nopriz_card['Сведения о наличии права'] \
                and nopriz_card['Размер взноса в компенсационный фонд возмещения вреда']:
            # Esli da, ishim ego v base nostroy
            for i, nostroy_card in enumerate(nostroy_data):
                if nostroy_card['ИНН'] == nopriz_card['ИНН']:
                    # Esli est udalyaem ego s dublikata nostroy
                    del nostroy_card[i]
                    logger.debug(f'NOSTROY card deleted: index - {i + 1}')
        else:
            # Esli net, ishim ego v base nostroy
            _include = False
            for i, nostroy_card in enumerate(nostroy_data):
                if nostroy_card['ИНН'] == nopriz_card['ИНН']:
                    _include = True
                    break
            if not _include:
                # Esli ego tam net dabavlyaem v dublickat nostroy
                nostroy_data.append(nopriz_card)
                logger.debug(f'Copy card from NOPRIZ to NOSTROY: index - {ii + 1}')
    logger.info(f'Sorted information count - {len(nostroy_data)}')
    logger.info(f'Wasted time: {datetime.now() - t0}')
    return nostroy_data

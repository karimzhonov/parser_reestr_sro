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
    return_data = []
    for card in logger.range(data, desc='Sort nostroy'):
        if (card['Статус члена'] and card['Сведения о наличии права']
                and card['Размер взноса в компенсационный фонд возмещения вреда']):
            return_data.append(card)
    logger.info(f'Sorted NOSTROY information count - {len(return_data)}')
    logger.info(f'Wasted time: {datetime.now() - t0}')
    return return_data


def sort_nopriz(nostroy_data: list[dict], nopriz_data: list[dict]):
    logger.info(f'NOSTROY Information count - {len(nostroy_data)}')
    logger.info(f'NOPRIZ Information count - {len(nopriz_data)}')
    # dublikat bazi nostroy
    append_data = []
    t0 = datetime.now()
    deleted_counter, copied_counter = 0, 0
    for ii, nopriz_card in enumerate(nopriz_data):
        # Praverka nopriz_card yavlyaetsali chlenom
        if nopriz_card['Статус члена'] and nopriz_card['Сведения о наличии права'] \
                and nopriz_card['Размер взноса в компенсационный фонд возмещения вреда']:
            # Esli da, ishim ego v base nostroy i udalyaem
            for i, nostroy_card in enumerate(nostroy_data):
                if nostroy_card['ИНН'] == nopriz_card['ИНН']:
                    deleted_counter += 1
                    nostroy_data.pop(i)
                    logger.info(f'Card deleted from NOSTROY: index - {i + 1}')
        else:
            # Esli net, ishim ego v base nostroy
            _include = False
            for i, nostroy_card in enumerate(nostroy_data):
                if nostroy_card['ИНН'] == nopriz_card['ИНН']:
                    _include = True
                    break
            if not _include:
                # Esli ego tam net dabavlyaem v dublickat nostroy
                copied_counter += 1
                append_data.append(nopriz_card)
                logger.info(f'Copy card from NOPRIZ to NOSTROY: index - {ii + 1}')
    return_data = [*nostroy_data, *append_data]
    logger.info(f'Deleted card from NOSTROY count: {deleted_counter}')
    logger.info(f'Copied card from NOPRIZ: {copied_counter}')
    logger.info(f'Sorted information count - {len(return_data)}')
    logger.info(f'Wasted time: {datetime.now() - t0}')
    return return_data

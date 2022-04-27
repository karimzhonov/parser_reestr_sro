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
import pandas as pd
from logger import logger


def sort_nostroy(data: pd.DataFrame):
    return_data = data[data['Статус члена'] &
                       data['Сведения о наличии права'] &
                       data['Размер взноса в компенсационный фонд возмещения вреда']]
    logger.info(f'Sorted NOSTROY information count - {len(return_data)}')
    return return_data


def sort_nopriz(nostroy_data: pd.DataFrame, nopriz_data: pd.DataFrame):
    logger.info(f'NOSTROY Information count - {len(nostroy_data)}')
    logger.info(f'NOPRIZ Information count - {len(nopriz_data)}')

    nopriz_data = nopriz_data[nopriz_data['Статус члена'] &
                              nopriz_data['Сведения о наличии права'] &
                              nopriz_data['Размер взноса в компенсационный фонд возмещения вреда']]
    # return_data = nopriz_data[nopriz_data['ИНН'].map(lambda value: len(nostroy_data[nostroy_data['ИНН'] == value]))]
    return_data = nostroy_data[nostroy_data.apply(lambda row: len(nopriz_data[nopriz_data['ИНН'] == row['ИНН']]) == 0, axis=1)]
    logger.info(f'Sorted information count - {len(return_data)}')
    return return_data

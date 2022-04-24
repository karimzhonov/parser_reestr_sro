import os
from excel import Excel
from logger import logger
from utils import get_datetime
from typer import Typer, Option
from scripts.sort_data import sort_nopriz, sort_nostroy

app = Typer()


@app.command()
def main(path: str = Option('./files/result', help="Path to dir which has 'nostroy.xlsx' and 'nopriz.xlsx' files"),
         log_level: int = Option(0, help='0 - ALL, 1 - warning, debug, error, 2 - warning, error, 3 - error')):
    """Sorter"""
    logger.set_level(log_level)
    if os.path.exists(path):
        nostroy_path = os.path.join(path, 'nostroy.xlsx')
        nopriz_path = os.path.join(path, 'nopriz.xlsx')
        if not os.path.exists(nostroy_path):
            logger.error(f'Cannot find file {nostroy_path}')
            return
        if not os.path.exists(nopriz_path):
            logger.error(f'Cannot find file {nopriz_path}')
            return
        nostroy_data = Excel.load(nostroy_path)
        nopriz_data = Excel.load(nopriz_path)
        # Sort Nostroy
        nostroy_data = sort_nostroy(nostroy_data)
        # Main sort
        data = sort_nopriz(nostroy_data, nopriz_data)
        # Save
        Excel.save(nostroy_data, os.path.join(path, f'Fayl-1_{get_datetime()}.xlsx'))
        Excel.save(data, os.path.join(path, f'Fayl-2_{get_datetime()}.xlsx'))
    else:
        logger.error(f'No such dir {path}')


if __name__ == '__main__':
    app()

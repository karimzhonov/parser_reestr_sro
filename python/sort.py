import os
from datetime import datetime
from excel import Excel
from typer import Typer, Option
from logger import logger
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
        t0 = datetime.now()
        nostroy_data = Excel.load_as_dataframe(nostroy_path)
        nostroy_data = sort_nostroy(nostroy_data)
        Excel.save_dataframe(nostroy_data, os.path.join(path, 'Fayl-1.xlsx'))

        nopriz_data = Excel.load_as_dataframe(nopriz_path)
        data = sort_nopriz(nostroy_data, nopriz_data)
        Excel.save_dataframe(data, os.path.join(path, f'Fayl-2.xlsx'))
        logger.info(f'Wasted time: {datetime.now() - t0}')
    else:
        logger.error(f'No such dir {path}')


if __name__ == '__main__':
    app()

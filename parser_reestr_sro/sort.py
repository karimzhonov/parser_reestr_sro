import os
from typer import Typer, Option
from excel import Excel
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

        nostroy_data = Excel.load(nostroy_path)
        nostroy_data = sort_nostroy(nostroy_data)
        Excel.save(nostroy_data, os.path.join(path, f'Fayl-1.xlsx'))

        nopriz_data = Excel.load(nopriz_path)
        data = sort_nopriz(nostroy_data, nopriz_data)
        Excel.save(data, os.path.join(path, f'Fayl-2.xlsx'))
    else:
        logger.error(f'No such dir {path}')


if __name__ == '__main__':
    app()

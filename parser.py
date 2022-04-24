import os
import asyncio
from logger import logger
from utils import get_datetime
from typer import Typer, Option
from scripts.async_reestr_nopriz import collect_data as nopriz_collect_data
from scripts.async_reestr_nostroy_ru import collect_data as nostroy_collect_data

app = Typer()

FOLDER_DIR = os.path.join(os.getcwd(), 'files')


async def _gather(mode: str = None, nostroy_async_chunk: int = None, nopriz_async_chunk: int = None,
                 nostroy_save_chunk: int = None, nopriz_save_chunk: int = None, folder_dir: str = FOLDER_DIR):
    if mode is None:
        await asyncio.gather(
            asyncio.create_task(nopriz_collect_data(os.path.join(folder_dir, f'nopriz.xlsx'), nopriz_save_chunk, nopriz_async_chunk)),
            asyncio.create_task(nostroy_collect_data(os.path.join(folder_dir, f'nostroy.xlsx'), nostroy_save_chunk, nostroy_async_chunk))
        )
    elif mode == 'nopriz':
        await asyncio.gather(
            asyncio.create_task(nopriz_collect_data(os.path.join(folder_dir, f'nopriz.xlsx'), nopriz_save_chunk, nopriz_async_chunk)),
        )
    elif mode == 'nostroy':
        await asyncio.gather(
            asyncio.create_task(nostroy_collect_data(os.path.join(folder_dir, f'nostroy.xlsx'), nostroy_save_chunk, nostroy_async_chunk)),
        )


@app.command()
def main(mode: str = Option(None, help='One of (nopriz, nostroy)'),
         log_level: int = Option(0, help='0 - ALL, 1 - warning, debug, error, 2 - warning, error, 3 - error'),
         save_path: str = Option(None, help='Path to save'),
         nostroy_async_chunk: int = Option(None, help='Count of async tasks'),
         nopriz_async_chunk: int = Option(None, help='Count of async tasks'),
         nostroy_save_chunk: int = Option(None, help='Max count of saving card while parsing'),
         nopriz_save_chunk: int = Option(None, help='Max count of saving card while parsing')):
    """Parser"""
    if save_path is None:
        # Make dir for result
        if not os.path.exists(FOLDER_DIR):
            os.mkdir(FOLDER_DIR)
        folder_dir = os.path.join(FOLDER_DIR, get_datetime())
        os.mkdir(folder_dir)
    else:
        folder_dir = save_path
    # Set log level
    logger.set_level(log_level)
    # Run Scripts
    asyncio.run(_gather(mode, nostroy_async_chunk, nopriz_async_chunk,
                       nostroy_save_chunk, nopriz_save_chunk, folder_dir))


if __name__ == '__main__':
    app()

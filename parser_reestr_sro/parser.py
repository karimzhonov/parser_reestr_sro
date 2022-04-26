import os
import sys
import asyncio
from typer import Typer, Option, Argument
from logger import logger
from utils import get_datetime
from scripts.reestr_nopriz import async_collect_data as nopriz_async_collect_data
from scripts.reestr_nostroy import async_collect_data as nostroy_async_collect_data
from scripts.reestr_nopriz import sync_collect_data as nopriz_sync_collect_data
from scripts.reestr_nostroy import sync_collect_data as nostroy_sync_collect_data

app = Typer()
FOLDER_DIR = os.path.join(os.getcwd(), 'files')

# Set Policy and logging
if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)


@app.command()
def main(mode: str = Argument(None, help='One of (async-nopriz, async-nostroy, sync-nopriz, sync-nostroy)'),
         log_level: int = 0,
         save_path: str = None,
         nostroy_async_chunk: int = 25,
         nopriz_async_chunk: int = 25,
         nostroy_save_chunk: int = 10000,
         nopriz_save_chunk: int = 10000):
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
    # Start
    if mode == 'async-nopriz':
        asyncio.run(
            nopriz_async_collect_data(os.path.join(folder_dir, f'nopriz.xlsx'), nopriz_save_chunk, nopriz_async_chunk))
    elif mode == 'async-nostroy':
        asyncio.run(nostroy_async_collect_data(os.path.join(folder_dir, f'nostroy.xlsx'), nostroy_save_chunk,
                                               nostroy_async_chunk))
    elif mode == 'sync-nostroy':
        nostroy_sync_collect_data(os.path.join(folder_dir, f'nostroy.xlsx'), nostroy_save_chunk)
    elif mode == 'sync-nopriz':
        nopriz_sync_collect_data(os.path.join(folder_dir, f'nopriz.xlsx'), nopriz_save_chunk)


if __name__ == '__main__':
    app()

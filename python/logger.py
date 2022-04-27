import datetime
from tqdm import tqdm


class Logger:
    DEBUG = True
    ERROR = True
    WARNING = True
    INFO = True

    @staticmethod
    def _datetime():
        return str(datetime.datetime.now()).split('.')[0]

    def _format(self, mode, msg):
        return f'[{mode}] - {self._datetime()} - {msg}'

    def _print(self, mode, *text, start, end, file):
        for t in text:
            print(f'{start}{self._format(mode, t)}', end=end, file=file)

    def debug(self, *text, start='', end='\n', file=None):
        if self.DEBUG:
            self._print('DEBUG', *text, end=end, file=file, start=start)

    def error(self, *text, start='', end='\n', file=None):
        if self.ERROR:
            self._print('ERROR', *text, end=end, file=file, start=start)

    def info(self, *text, start='', end='\n', file=None):
        if self.INFO:
            self._print('INFO', *text, end=end, file=file, start=start)

    def warning(self, *text, start='', end='\n', file=None):
        if self.WARNING:
            self._print('WARNING', *text, end=end, file=file, start=start)

    def range(self, range_func, desc='', **kwargs):
        desc = self._format('DEBUG', desc)
        return tqdm(range_func, desc=desc, **kwargs) if self.DEBUG else range_func

    def set_level(self, level: int):
        """0 - ALL, 1 - warning, debug, error, 2 - warning, error, 3 - error"""
        if not isinstance(level, int): return
        if level == 1:
            self.INFO = False
            self.DEBUG = True
            self.WARNING = True
            self.ERROR = True
        elif level == 2:
            self.INFO = False
            self.DEBUG = False
            self.WARNING = True
            self.ERROR = True
        elif level == 3:
            self.INFO = False
            self.DEBUG = False
            self.WARNING = False
            self.ERROR = True
        else:
            self.INFO = True
            self.DEBUG = True
            self.WARNING = True
            self.ERROR = True


logger = Logger()

import sys
import traceback
from collections import defaultdict
from datetime import datetime, timedelta
import logging

class Counter:
    def __init__(self):
        self.dict = defaultdict(int)

    def __call__(self, x):
        if not x:
            return False
        self.dict[int(x)] += 1
        return True

    def order_list(self, kn='id', vn='count', rev=False):
        return sorted([{kn: x, vn: count} for x, count in self.dict.items()], key=lambda x: x['count'], reverse=rev)

    def reset(self):
        self.dict.clear()


def interpolation(data, n=30):
    """
    为 news_statistic_by_date 插值
    data: [{'date': str, 'count': int}, ...]
    """
    if len(data) >= 2:
        begin_date = datetime.strptime(data[0]['date'], '%Y-%m')
        end_date = datetime.strptime(data[-1]['date'], '%Y-%m')
        
        months = (end_date - begin_date).days // 30

        interval = max(1, months // n) * 31

        final_data = [{'date': datetime.strftime(datetime.strptime(data[0]['date'], '%Y-%m') - timedelta(days=interval), '%Y-%m'), 'count': 0}]
        next_date = data[0]['date']
        i = 0
        while i < len(data):
            if next_date < data[i]['date']:
                final_data.append({'date': next_date, 'count': 0})
                next_date = datetime.strftime(datetime.strptime(next_date, '%Y-%m') + timedelta(days=interval), '%Y-%m')
            elif next_date == data[i]['date']:
                final_data.append(data[i])
                next_date = datetime.strftime(datetime.strptime(next_date, '%Y-%m') + timedelta(days=interval), '%Y-%m')
                i += 1
            else:
                final_data.append(data[i])
                i += 1
    else:
        final_data = [{'date': datetime.now().strftime('%Y-%m'), 'count': 0}]

    return final_data


def brief_path(verbose_path):
    stripped = verbose_path
    for env_var in sys.path:
        stripped = verbose_path.replace(env_var, '')
        if stripped != verbose_path:
            return stripped.lstrip('/\\')
    return stripped


class Logger:
    """
    name: name of logger
    filename: if specified, log will be written into the file
    silent: no output at terminal if `True`
    """
    default_level = 'debug'

    @staticmethod
    def level_filter(level):
        return lambda record: record.levelname == level.upper()

    def __init__(self, name=__file__, level=default_level, filename=None, silent=False, datefmt='%Y-%m-%d %H:%M:%S'):
        """
        name: name of logger
        filename: if specified, log will be written into the file
        silent: no output at terminal if `True`
        """
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt=datefmt)
        self.logger = logging.getLogger(name)
        self.logger.setLevel('DEBUG')

        if isinstance(filename, str):
            self.add_handler(filename, level=level)
        elif isinstance(filename, dict):
            for level, name in filename.items():
                # this will not work, `level` below is not that `level` above
                # self.add_handler(filename=name, level_filter=lambda record: record.levelname == level.upper())
                self.add_handler(filename=name, level_filter=self.__class__.level_filter(level))
        if not silent:
            self.add_handler()

    def add_handler(self, filename=None, level=default_level, level_filter=None):
        if type(filename) == str and filename:
            handler = logging.FileHandler(filename, encoding='utf-8')
        else:
            handler = logging.StreamHandler()
        handler.setFormatter(self.formatter)
        if level_filter:
            handler.addFilter(level_filter)
        else:
            handler.setLevel(level.upper())
        self.logger.addHandler(handler)
    
    def error(self, message='', exc_info=None):
        """
        message: error message
        exc_info: tuple returned by sys.exc_info()
        """
        if exc_info:
            exc_type, exc_value, exc_traceback = exc_info
            additional = f'[{message}] ' if message else ''
            self.logger.error(additional + ' => '.join([f'"{brief_path(fs.filename)}", {fs.lineno}: "{fs.line}"' for fs in traceback.extract_tb(exc_traceback)]) + f' [{exc_type.__name__}: {exc_value}]')
        else:
            self.logger.error(message)
    
    def info(self, message=''):
        self.logger.info(message)
    
    def warning(self, message=''):
        self.logger.warning(message)

    def debug(self, message=''):
        self.logger.debug(message)

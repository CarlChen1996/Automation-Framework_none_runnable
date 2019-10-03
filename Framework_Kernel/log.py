# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:22 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : log.py
# @Project : Automation-Framework
import multiprocessing
import os
import time
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from PIL import ImageGrab
import yaml

lock = multiprocessing.Lock()
with open(os.path.join(os.getcwd() + r'/Configuration/config_framework_list.yml'), 'r', encoding='utf-8') as f:
    log_settings = yaml.safe_load(f.read())['log_settings']


class SafeLog(TimedRotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super(SafeLog, self).__init__(*args, **kwargs)
        self.suffix_time = ""
        self.origin_basename = self.baseFilename

    def shouldRollover(self, record):
        time_tuple = time.localtime()
        if self.suffix_time != time.strftime(self.suffix, time_tuple) or not os.path.exists(
                self.origin_basename + '.' + self.suffix_time):
            return 1
        else:
            return 0

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        current_time_tuple = time.localtime()
        self.suffix_time = time.strftime(self.suffix, current_time_tuple)
        self.baseFilename = self.origin_basename + '.' + self.suffix_time

        self.mode = 'a'

        global lock
        with lock:
            if self.backupCount > 0:
                for s in self.getFilesToDelete():
                    os.remove(s)

        if not self.delay:
            self.stream = self._open()

    def getFilesToDelete(self):
        # rename self.baseFilename to self.origin_basename
        dir_name, base_name = os.path.split(self.origin_basename)
        file_name_list = os.listdir(dir_name)
        result = []
        prefix = base_name + "."
        plen = len(prefix)
        for file_name in file_name_list:
            if file_name[:plen] == prefix:
                suffix = file_name[plen:]
                if self.extMatch.match(suffix):
                    result.append(os.path.join(dir_name, file_name))
        if len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backupCount]
        return result


class Log:
    def __init__(self, name=log_settings['NAME'], default_settings=log_settings):
        self.__name = name
        self.__type = log_settings['log_type']
        self.__level = log_settings['log_level']
        self.separator = log_settings['log_seperator']
        self.if_screenshot = log_settings['if_screenshot']
        self.use_console = log_settings['use_console']
        self.log_path = os.path.join(
            os.getcwd(),
            'Log\\{}\\{}\\'.format(time.strftime(log_settings['log_path'], time.localtime()), self.__name)
        )
        self.logger = logging.getLogger(name)
        '''
                    name： name will print in log，default:''
                    level： set log print level，default:DEBUG
                    log_path： log file folder path
                    use_console： print on console or not, default:True
                    separator: custom separator
                    if_screenshot: take screenshot while print log
        '''
        if self.__level.lower() == "critical":
            self.logger.setLevel(logging.CRITICAL)
        elif self.__level.lower() == "error":
            self.logger.setLevel(logging.ERROR)
        elif self.__level.lower() == "warning":
            self.logger.setLevel(logging.WARNING)
        elif self.__level.lower() == "info":
            self.logger.setLevel(logging.INFO)
        elif self.__level.lower() == "debug":
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.NOTSET)

        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        log_handler = SafeLog(self.log_path + self.__name, when=log_settings['when'], interval=log_settings['interval'],
                              backupCount=log_settings['backup_count'], encoding='utf-8')
        log_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] {} %(name)s {} [%(levelname)s] {} %(message)s".format(self.separator, self.separator,
                                                                                     self.separator)))
        self.logger.addHandler(log_handler)
        if self.use_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(
                "[%(asctime)s] {} %(name)s {} [%(levelname)s] {} %(message)s".format(self.separator, self.separator,
                                                                                     self.separator)))
            self.logger.addHandler(console_handler)

    def screenshot(self, screenshot=False):
        if screenshot is True:
            screenshot = ImageGrab.grab()
            snap_path = os.path.join(self.log_path + 'screenshot')
            if not os.path.exists(snap_path):
                os.makedirs(snap_path)
            snap_file_path = snap_path + '\\{}.jpg'.format(datetime.datetime.now().strftime('%H-%M-%S.%f'))
            screenshot.save(snap_file_path)

    def add_handler(self, hdlr):
        self.logger.addHandler(hdlr)

    def remove_handler(self, hdlr):
        self.logger.removeHandler(hdlr)

    def critical(self, msg, *args, **kwargs):
        if self.if_screenshot:
            self.screenshot(screenshot=True)
        self.logger.critical(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.if_screenshot:
            self.screenshot(screenshot=True)
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.if_screenshot:
            self.screenshot(screenshot=True)
        self.logger.error(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if self.if_screenshot:
            self.screenshot(screenshot=True)
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        if self.if_screenshot:
            self.screenshot(screenshot=True)
        self.logger.debug(msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        if self.if_screenshot:
            self.screenshot(screenshot=True)
        self.logger.log(level, msg, *args, **kwargs)


controller_log = Log(name='controller')
execution_log = Log(name='execution_engine')
configuration_log = Log(name='configuration_engine')
assemble_log = Log(name='assemble_engine')
error_handler_log = Log(name="error_handler")

if __name__ == '__main__':
    assemble_log.info('test')

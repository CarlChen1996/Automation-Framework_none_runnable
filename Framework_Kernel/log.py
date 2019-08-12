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
with open(os.path.join(os.getcwd() + r'/Configuration/config_log.yml'), 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f.read())
# with open(os.path.join(os.path.dirname(os.getcwd()) + r'/Configuration/config_log.yml'), 'r', encoding='utf-8') as f:
#     config = yaml.safe_load(f.read())

class SafeLog(TimedRotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super(SafeLog, self).__init__(*args, **kwargs)
        self.suffix_time = ""
        self.origin_basename = self.baseFilename


    def shouldRollover(self, record):
        timeTuple = time.localtime()
        if self.suffix_time != time.strftime(self.suffix, timeTuple) or not os.path.exists(self.origin_basename+'.'+self.suffix_time):
            return 1
        else:
            return 0

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        currentTimeTuple = time.localtime()
        self.suffix_time = time.strftime(self.suffix, currentTimeTuple)
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
        #rename self.baseFilename to self.origin_basename
        dirName, baseName = os.path.split(self.origin_basename)
        fileNames = os.listdir(dirName)
        result = []
        prefix = baseName + "."
        plen = len(prefix)
        for fileName in fileNames:
            if fileName[:plen] == prefix:
                suffix = fileName[plen:]
                if self.extMatch.match(suffix):
                    result.append(os.path.join(dirName, fileName))
        if len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backupCount]
        return result


class Log:
    def __init__(self, name=config['NAME'], log_type=config['LOG_TYPE'], level=config['LEVEL'], separator=config['SEPARATOR'], use_console=config['USE_CONSOLE'], if_screenshot=config['IF_SCREENSHOT'], log_path=config['LOG_PATH']):
        self.__name = name
        self.__type = log_type
        self.__level = level
        self.separator = separator
        self.if_screenshot = if_screenshot
        self.log_path = os.path.join(
                                    os.getcwd(),
                                    'Log\\{}\\{}\\'.format(time.strftime(log_path, time.localtime()),self.__name)
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
        if level.lower() == "critical":
            self.logger.setLevel(logging.CRITICAL)
        elif level.lower() == "error":
            self.logger.setLevel(logging.ERROR)
        elif level.lower() == "warning":
            self.logger.setLevel(logging.WARNING)
        elif level.lower() == "info":
            self.logger.setLevel(logging.INFO)
        elif level.lower() == "debug":
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.NOTSET)

        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        # log_file_path = self.log_path + '{}.log'.format(self.__name)
        log_handler = SafeLog(self.log_path+self.__name, when=config['WHEN'], interval=config['INTERVAL'], backupCount=config['BACKUP_COUNT'], encoding='utf-8')
        # log_handler.suffix = "%Y-%m-%d_%H-%M-%S.log"
        log_handler.setFormatter(
            logging.Formatter("[%(asctime)s] {} %(name)s {} [%(levelname)s] {} %(message)s".format(self.separator, self.separator, self.separator)))
        self.logger.addHandler(log_handler)
        if use_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter("[%(asctime)s] {} %(name)s {} [%(levelname)s] {} %(message)s".format(self.separator, self.separator, self.separator)))
            self.logger.addHandler(console_handler)

    def screenshot(self,screenshot=False):
        if screenshot==True:
            screenshot = ImageGrab.grab()
            snap_path = os.path.join(self.log_path +'screenshot')
            if not os.path.exists(snap_path):
                os.makedirs(snap_path)
            snap_file_path = snap_path + '\\{}.jpg'.format(datetime.datetime.now().strftime('%H-%M-%S.%f'))
            screenshot.save(snap_file_path)

    def addHandler(self, hdlr):
        self.logger.addHandler(hdlr)

    def removeHandler(self, hdlr):
        self.logger.removeHandler(hdlr)

    def critical(self, msg, *args, **kwargs):
        if self.if_screenshot==True:
            self.screenshot(screenshot=True)
        self.logger.critical(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.if_screenshot==True:
            self.screenshot(screenshot=True)
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.if_screenshot==True:
            self.screenshot(screenshot=True)
        self.logger.error(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if self.if_screenshot==True:
            self.screenshot(screenshot=True)
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        if self.if_screenshot==True:
            self.screenshot(screenshot=True)
        self.logger.debug(msg, *args, **kwargs)

    def log(self, level, msg,  *args, **kwargs):
        if self.if_screenshot==True:
            self.screenshot(screenshot=True)
        self.logger.log(level, msg, *args, **kwargs)


controller_log = Log(name='controller')
execution_log = Log(name='execution_engine')
# # execution_log = Log(name='execution_engine',if_screenshot=True,separator='?')
configuration_log = Log(name='configuration_engine')
assemble_log = Log(name='assemble_engine')

if __name__ == '__main__':
    with open(os.path.join(os.getcwd()+'\\Configuration\\config_log.yml'),'r',encoding='utf-8') as f:
        d = yaml.safe_load(f.read())
    print(d)





# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:22 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : log.py
# @Project : Automation-Framework
import os
import time
import datetime
import logging
import logging.handlers as lh
from PIL import ImageGrab
from Configuration.settings import *


class Log:
    def __init__(self, name=NAME, log_type=LOG_TYPE, level=LEVEL, separator=SEPARATOR, use_console=USE_CONSOLE, if_screenshot=IF_SCREENSHOT, log_path=LOG_PATH):
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

                    name： 日志中将会打印的name，默认为运行程序的name
                    level： 设置日志的<打印>级别，默认为DEBUG
                    log_path： 日志文件夹的路径，默认为同级目录中的log文件夹
                    use_console： 是否在控制台打印，默认为True
                    separator: 自定义分隔符
                    if_screenshot:写日志同时是否截图
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
        log_handler = lh.TimedRotatingFileHandler(self.log_path+self.__name, when=WHEN, interval=INTERVAL, backupCount=BACKUP_COUNT, encoding='utf-8')
        log_handler.suffix = "%H_%M_%S.log"
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
# execution_log = Log(name='execution_engine',if_screenshot=True,separator='?')
assemble_log = Log(name='assemble_engine')
configuration_log = Log(name='configuration_engine')


if __name__ == '__main__':
    l = Log(name='test',if_screenshot=False)
    l.info('213124')
    for i in range(5):
        l.info('test')
        time.sleep(1)
    l.if_screenshot=True
    l.log(10,'cnm')
    assemble_log.if_screenshot=True
    for i in range(3):
        assemble_log.log(20,'hhhhahahaahahaha')
        assemble_log.info('test')
        time.sleep(1)
    l.screenshot(True)





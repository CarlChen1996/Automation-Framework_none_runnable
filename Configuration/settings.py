# -*- coding: utf-8 -*-
# @Time    : 7/25/2019 1:54 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : settings.py.py
# @Project : Automation-Framework

# Default log setting
NAME = ''
LOG_TYPE = 'default'
LEVEL = 'debug'
SEPARATOR = '-'
USE_CONSOLE = True
IF_SCREENSHOT = False
'''
Start moment
'''
# LOG_PATH = "%Y-%m-%d_%H-%M-%S"
# LOG_PATH = "%Y-%m-%d_%H-%M"
LOG_PATH = "%Y-%m-%d_%H"
'''
TimedRotatingFileHandler
    WHEN:
        # S - Seconds
        # M - Minutes
        # H - Hours
        # D - Days
        # midnight - roll over at midnight
        # W{0-6} - roll over on a certain day; 0 - Monday

'''
# 1 hour 1 file, no count limit
WHEN = 'H'
INTERVAL = 1
BACKUP_COUNT = 0
#

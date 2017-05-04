#-*- coding: utf-8 -*-

import logging
import traceback
import datetime
import platform
import os

from bs4 import CData
from bs4 import NavigableString


def make_dir(dir):
    log('make dir:%s' % dir)
    if not os.path.exists(dir):
        os.makedirs(dir)


def log(msg, level = logging.DEBUG):
    logging.log(level, msg)
    print('%s [level:%s] msg:%s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), level, msg))

    if level == logging.WARNING or level == logging.ERROR:
        for line in traceback.format_stack():
            print(line.strip())

        for line in traceback.format_stack():
            logging.log(level, line.strip())


def get_first_text(soup, strip = False, types = (NavigableString, CData)):
    data = None
    for s in soup._all_strings(strip, types = types):
        data = s
        break
    return data


def get_texts(soup, strip = False, types = (NavigableString, CData)):
    texts = []
    for s in soup._all_strings(strip, types = types):
        texts.append(s)

    return texts


def get_platform():
    plat = platform.platform()
    if plat.find('Darwin') != -1:
        return 'mac'
    elif plat.find('Linux') != -1:
        return 'linux'
    else:
        return 'mac'


def get_date():
    return datetime.datetime.today().strftime('%Y-%m-%d')



def key_print(msg):
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print ""
    print msg
    print ""
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# common
import os, sys
import traceback


# logging
import logging


# smart_dumps
from .smart_json import smart_dumps


# ansi
from .ansi import ANSIFmt, ANSINoFmt



class MyLogger(logging.Logger):

    def __init__(self, name, level = logging.NOTSET):
        LOG_WITH_FORMATTING = os.environ.get('LOG_WITH_FORMATTING', 'true').lower()
        if LOG_WITH_FORMATTING == 'true':
            self.ANSIFmt = ANSIFmt
        else:
            self.ANSIFmt = ANSINoFmt

        return super(MyLogger, self).__init__(name, level)


    def nothing(self, *args, **kwargs):
        pass

    def green(self, msg, submsg='',*args, **kwargs):

        if type(submsg) in [dict,list,tuple]:
            submsg = smart_dumps(submsg)

        return super(MyLogger, self).info(
            r'{0}{1}{2}{3} {4}'.format(
                self.ANSIFmt.green,
                self.ANSIFmt.bold,
                msg,
                self.ANSIFmt.reset,
                submsg,
            ),
            *args,
            **kwargs,
        )

    def blue(self, msg, submsg='',*args, **kwargs):

        if type(submsg) in [dict,list,tuple]:
            submsg = smart_dumps(submsg)

        return super(MyLogger, self).info(
            r'{0}{1}{2}{3} {4}'.format(
                self.ANSIFmt.blue,
                self.ANSIFmt.bold,
                msg,
                self.ANSIFmt.reset,
                submsg,
            ),
            *args,
            **kwargs,
        )

    def cyan(self, msg, submsg='',*args, **kwargs):

        if type(submsg) in [dict,list,tuple]:
            submsg = smart_dumps(submsg)

        return super(MyLogger, self).info(
            r'{0}{1}{2}{3} {4}'.format(
                self.ANSIFmt.cyan,
                self.ANSIFmt.bold,
                msg,
                self.ANSIFmt.reset,
                submsg,
            ),
            *args,
            **kwargs,
        )


    def normal(self, msg, submsg='',*args, **kwargs):

        if type(submsg) in [dict,list,tuple]:
            submsg = smart_dumps(submsg)

        return super(MyLogger, self).info(
            r'{0} {1}'.format(
                msg,
                submsg,
            ),
            *args,
            **kwargs,
        )


    def warning(self, msg, submsg='',*args, **kwargs):

        if type(submsg) in [dict,list,tuple]:
            submsg = smart_dumps(submsg)

        return super(MyLogger, self).warning(
            r'{0}{1}{2}{3} {4}'.format(
                self.ANSIFmt.yellow,
                self.ANSIFmt.bold,
                msg,
                self.ANSIFmt.reset,
                submsg,
            ),
            *args,
            **kwargs,
        )

    def error(self, msg, submsg='',*args, **kwargs):

        if type(submsg) in [dict,list,tuple]:
            submsg = smart_dumps(submsg)

        return super(MyLogger, self).error(
            r'{0}{1}{2}{3} {4}'.format(
                self.ANSIFmt.red,
                self.ANSIFmt.bold,
                msg,
                self.ANSIFmt.reset,
                submsg,
            ),
            *args,
            **kwargs,
        )

    def critical(self, msg, submsg='',*args, **kwargs):

        if type(submsg) in [dict,list,tuple]:
            submsg = smart_dumps(submsg)

        return super(MyLogger, self).critical(
            r'{0}{1}{2}{3} {4}'.format(
                self.ANSIFmt.red,
                self.ANSIFmt.bold,
                msg,
                self.ANSIFmt.reset,
                submsg,
            ),
            *args,
            **kwargs,
        )


def getLogger(logger_name):

    LOG_LEVEL     = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_WITH_FORMATTING = os.environ.get('LOG_WITH_FORMATTING', 'true').lower()
    PROCESS_LEVEL = os.environ.get('PROCESS_LEVEL', '1')
    PROCESS_LEVEL = int(PROCESS_LEVEL) - 1

    # custom function
    if LOG_WITH_FORMATTING == 'true':
        logging.setLoggerClass(MyLogger)
    else:
        logging.setLoggerClass(MyLogger)

    # get logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOG_LEVEL)
    logger.propagate = False

    # formatter
    if LOG_WITH_FORMATTING == 'true':
        format_str = r'{0}%(asctime)s <%(name)s>{1} {2}%(message)s'.format(
            ANSIFmt.gray,
            ANSIFmt.reset,
            ANSIFmt.cyan + '└───'*PROCESS_LEVEL + ANSIFmt.reset,
        )
    else:
        format_str = r'%(asctime)s <%(name)s>{0}%(levelname)s %(message)s'.format(
            '└───'*PROCESS_LEVEL
        )

    formatter = logging.Formatter(format_str)

    # # clear handlers
    logger.handlers = []

    # stream handler
    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger

#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)



class ANSIFmt:
    reset           = '\033' + '[0m'
    bold            = '\033' + '[01m'
    disable         = '\033' + '[02m'
    underline       = '\033' + '[04m'
    reverse         = '\033' + '[07m'
    strikethrough   = '\033' + '[09m'
    invisible       = '\033' + '[08m'

    no_color        = ''
    red             = '\033' + '[31m'
    green           = '\033' + '[32m'
    yellow          = '\033' + '[33m'
    blue            = '\033' + '[34m'
    gray            = '\033' + '[38;5;243m'
    cyan            = '\033' + '[38;5;35m'

class ANSINoFmt:
    reset           = ''
    bold            = ''
    disable         = ''
    underline       = ''
    reverse         = ''
    strikethrough   = ''
    invisible       = ''

    no_color        = ''
    red             = ''
    green           = ''
    yellow          = ''
    blue            = ''
    gray            = ''
    cyan            = ''
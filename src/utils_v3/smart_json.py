#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# common
import os, sys
import traceback
import time


# technical
import json
import re


# ansi
from .ansi import ANSIFmt, ANSINoFmt


# envs:
Hsb_2_Bracket = {
    list  : '[]',
    tuple : '()',
    set   : '{}',
}


Configs = {

    'indent'    : int(os.getenv('SMART_DUMPS__INDENT', 4)),

    'head_size' : int(os.getenv('SMART_DUMPS__HEAD_SIZE', 22)),
    'tail_size' : int(os.getenv('SMART_DUMPS__TAIL_SIZE', 2)),

    'left_size' : int(os.getenv('SMART_DUMPS__LEFT_SIZE', 220)),
    'rite_size' : int(os.getenv('SMART_DUMPS__RITE_SIZE', 20)),

}



def smart_dumps(
    Data,
    indent=Configs['indent'],
    head_size=Configs['head_size'],
    tail_size=Configs['tail_size'],
    left_size=Configs['left_size'],
    rite_size=Configs['rite_size'],
    strip_color_codes=False,
):

    # stage -1
    if strip_color_codes:
        ANSI_Formatter = ANSINoFmt
    else:
        ANSI_Formatter = ANSIFmt


    # stage 0
    if type(Data) not in [dict, list, tuple, set]:
        return str(Data)

    # stage 1
    indent_str = ' ' * indent
    max_vert_size = head_size + tail_size
    max_horz_size = left_size + rite_size

    # stage 2
    if type(Data) in [list, tuple, set]:
        Dumped = '{}\n'.format(Hsb_2_Bracket[type(Data)][0])

        for datum in Data:
            Dumped += indent_str + smart_dumps(datum).replace('\n', '\n'+indent_str)
            Dumped = Dumped.rstrip() + ',\n'

        Dumped = Dumped[:-2] + '\n{}\n'.format(Hsb_2_Bracket[type(Data)][1])

        return Dumped


    # stage 3
    Dumped = '{\n'

    for key, Value in Data.items():

        # stage 0
        try:
            Value_Dumped_Lines =  json.dumps(
                Value,
                indent=indent,
                ensure_ascii=False,
            ).split('\n')
        except:
            Value_Dumped_Lines = ['"{}"'.format(Value)]


        # stage 1
        for i, line in enumerate(Value_Dumped_Lines):
            if len(line) > max_horz_size:
                More_Horz_Lines = ANSI_Formatter.yellow + ANSI_Formatter.bold + ' ├───── + {} CHARS ─────┤ '.format(len(line) - max_horz_size) + ANSI_Formatter.reset
                Value_Dumped_Lines[i] = line[:left_size] + More_Horz_Lines + line[-rite_size:]


        # stage 2
        if len(Value_Dumped_Lines) > max_vert_size:

            More_Vert_Lines = [
                indent_str + '︰',
                indent_str + '︰',
                indent_str + '︰ + {} LINES'.format(len(Value_Dumped_Lines) - max_vert_size),
                indent_str + '︰',
                indent_str + '︰',
            ]

            for i in range(len(More_Vert_Lines)):
                More_Vert_Lines[i] = ANSI_Formatter.yellow + ANSI_Formatter.bold + More_Vert_Lines[i] + ANSI_Formatter.reset

            Value_Dumped_Lines = Value_Dumped_Lines[:head_size] + More_Vert_Lines + Value_Dumped_Lines[-tail_size:]


        # stage 3
        Dumped += '{0}"{1}": {2},\n'.format(
            ' '*indent,
            key,
            '\n{}'.format(' '*indent).join(Value_Dumped_Lines)
        )

    if len(Dumped) > 2:
        Dumped = Dumped[:-2] + '\n}\n'
    else:
        Dumped = None

    return Dumped


def test():

    from .profiler import lap

    lap()

    with open('exp/Thoi_Su.final.json','r') as f:
        some_dict = json.load(f)

    lap()

    print(
        smart_dumps(some_dict)
    )

    lap()


if __name__ == '__main__':
    test()

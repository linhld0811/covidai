#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# common
import os, sys
import traceback


# technical
import selectors
import shlex
import subprocess


# logger
from .logger import getLogger
logger = getLogger(__name__)


# strip_color_codes
from .strip_color_codes import strip_color_codes



def shlex_split(cmd):
    Lines = []
    for line in cmd.split('\n'):
        if line.strip(): Lines.append(line)

    # stage 1
    New_Lines = []

    for line in reversed(Lines):
        if line[-1] == '\\':
            New_Lines[-1] =  '\t'+line.lstrip() + '\n' + New_Lines[-1]
        else:
            New_Lines.append('\t'+line.lstrip())

    New_Lines = list(reversed(New_Lines))

    # stage 2
    for i in range(len(New_Lines)):
        New_Lines[i] = New_Lines[i].lstrip().split(' ', 1)
        if len(New_Lines[i]) == 1:
            New_Lines[i] += ['']

    return New_Lines


def bash(
    cmd,
    silent=False,
    strip=True,
    traceback__stdout_limit=40,
    traceback__stderr_limit=40,
    cwd=None,
):

    for split in shlex_split(cmd):

        if split[1].count('\n') > 0:
            split[1] += '\n'

        if not silent:
            logger.cyan(
                '└───●[{}'.format(split[0]),
                '{}]'.format(split[1]),
            )

    # My_Env = os.environ.copy()
    # My_Env["LOG_WITH_FORMATTING"] = "false"

    process = subprocess.Popen(
        cmd,
        shell=True,
        executable='/bin/bash',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
    )

    sel = selectors.DefaultSelector()
    sel.register(process.stdout, selectors.EVENT_READ)
    sel.register(process.stderr, selectors.EVENT_READ)

    StdOut_Agg = ''
    StdErr_Agg = ''

    ok = True
    while ok:
        for key, _ in sel.select():
            data = key.fileobj.read1().decode()

            if not data:
                ok = False
                break

            if key.fileobj is process.stdout:
                StdOut_Agg += data
                if not silent:
                    print(data, end='', file=sys.stdout, flush=True)

            if key.fileobj is process.stderr:
                StdErr_Agg += data
                if not silent:
                    print(data, end='', file=sys.stderr, flush=True)

    process.wait()

    if process.returncode !=0:

        traceback_str__Lines =  [ ' ',
                                  '+ cmd: {}'.format(cmd),
                                  '+ returncode: {}'.format(process.returncode) ]

        traceback_str__Lines += [ '+ truncated StdOut:' ]
        traceback_str__Lines += strip_color_codes(StdOut_Agg).split('\n')[-traceback__stdout_limit-1:]

        traceback_str__Lines += [ '+ truncated StdErr:' ]
        traceback_str__Lines += strip_color_codes(StdErr_Agg).split('\n')[-traceback__stderr_limit-1:]

        traceback_str = '\n'.join(traceback_str__Lines)

        raise Exception(traceback_str)

    if strip:
        StdOut_Agg = StdOut_Agg.strip()
        StdErr_Agg = StdErr_Agg.strip()

    return StdOut_Agg, StdErr_Agg



# SOME APPLICATIONS
def get_shell_var_value(script, var):
    cmd = 'source \"{}\" && echo \"${}\"'.format(script, var)
    stdout, *_ = bash(cmd, strip=True)
    return stdout


def get_line_count(inp_text_file):
    stdout, *_ = bash('cat {} | wc -l'.format(inp_text_file), silent=True)
    return int(stdout.strip())

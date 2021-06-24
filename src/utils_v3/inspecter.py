#!/usr/bin/env python3

# Copyright 2020 Lam Nguyen


# common
import os, sys
import traceback


# technical
import json
try:
    import numpy as np
except:
    np = None


# logger
from .logger import getLogger
logger = getLogger(__name__)


# bash
from .easy_basher import bash



def get_obj_size(obj, seen=None):
    """
    Thanks to: https://github.com/bosswissam
    Recursively finds size of objects
    """
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


def get_node_size(node):

    node_size = bash(r'du -sb "{0}"'.format(node), silent=True)[0]
    node_size = int(node_size.split(maxsplit=1)[0])

    return node_size


def file_or_dir(node):

    if os.path.isdir(node):
        return 'dir'

    elif os.path.isfile(node):
        return 'file'

    else:
        return 'none'


def get_mime_type(file):

    ret, _ = bash(r'''
        file --mime-type "{0}" | awk '{{print $NF}}'
    '''.format(file), silent=True)

    return ret.strip()


def get_dur_by_ffmpeg(file):

    ret, _ = bash(r'''
        ffprobe -v quiet -show_format -hide_banner -i "{0}" \
            | sed -n 's/duration=//p' \
            | xargs printf %.3f
    '''.format(file), silent=True, strip=True)

    return float(ret)


def get_dur_by_sox(file):

    ret, _ = bash(r'''
        soxi -D "{0}"
    '''.format(file), silent=True, strip=True)

    return float(ret)


def get_stats(var, var_name="unknown", depth=0):

    try:
        stats = {}
        stats['var_name'] = var_name
        stats['size'] = str(sys.getsizeof(var)/1024) + " KB"
        stats['type'] = str(type(var))

        if type(var) is list:
            stats['len'] = str(len(var))
            stats['1st item'] = get_stats(var[0], var_name=var_name+'[0]', depth=depth+1)

        if type(var) is dict:
            stats['key_count'] = str(len(var.keys()))
            stats['1st item'] = get_stats(var[list(var.keys())[0]], var_name=var_name+'[\'' + str(list(var.keys())[0]) +'\']', depth=depth+1)

        if np:
            if type(var) is np.ndarray:
                stats['shape'] = str(var.shape)
                stats['dtype'] = str(var.dtype)

            if type(var) is np.lib.npyio.NpzFile:
                stats['files'] = str(var.files)
                for f in var.files:
                    stats[var_name+'['+f+']'] = get_stats(var[f], var_name=var_name+'[\''+f+'\']', depth=depth+1)

    except:
        logger.error(traceback.format_exc())
        return False

    return stats


def print_stats(var, var_name="unknown"):

    stats = get_stats(var, var_name)
    logger.info(json.dumps(stats, indent=4))

    return

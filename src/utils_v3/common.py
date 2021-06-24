#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# common
import os, sys
import traceback
import time


# technical
from datetime import datetime
from pathlib import Path
import pickle
import json
import re
import shutil
import unicodedata
import uuid


# logger
from .logger import getLogger
logger = getLogger(__name__)


# bash
from .easy_basher import bash


# print_stats
from .inspecter import print_stats



# ==================================================
#                    TIMING
# ==================================================
def get_timestamp():
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]


def get_timeslug():
    return datetime.utcnow().strftime('%Y.%m.%d__%Hh%Mm%Ss.%f')[:-3]


def get_modified_epoch_time(inp_file):
    return int(bash('stat -c "%Z" {}'.format(inp_file), silent=True)[0])



# ==================================================
#                STRING MANIPULATIONS
# ==================================================
def rstrip(inp_string, removed_string):
    return inp_string[ : -len(removed_string) ]


def lstrip(inp_string, removed_string):
    return inp_string[ len(removed_string) : ]


def slugify(value):
    """
    Adapted from : https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


def slugify_v2(value):
    """
    The same as slugify() but without removing dots and de-captitalization.
    """
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^.\w\s-]', '', value).strip()
    return re.sub(r'[-\s]+', '-', value)



# ==================================================
#                 FILE/DIR MANIPULATIONS
# ==================================================
def archive(source):

    timestamp = datetime.now().strftime('%Y_%m_%d-%H_%M_%S-%f')

    if not os.path.exists(source):
        if os.path.islink(source):
            logger.warning('Removing invalid symlink:', source)
            os.remove(source)

        logger.info('Skipping')
        return True

    source = os.path.abspath(source)

    target = os.path.join(
        Path(source).parent,
        '__archived__',
        timestamp + '-' + Path(source).name,
    )

    if os.path.exists(target):
        logger.info('Skipping')
        return True

    os.makedirs(Path(target).parent, exist_ok=True)
    shutil.move(source, target)
    logger.green('Archived:', r'{} --archived--> {}'.format(source, target))

    return True


def recreate(source):

    if os.path.exists(source):
        if not os.path.isdir(source):
            return False

    source = os.path.abspath(source)

    archive(source)
    os.makedirs(source, exist_ok=False)
    logger.info("RECREATED: {} --recreated--> {}".format(source, source))

    return True


def symlink(source, target):

    if not os.path.exists(source):
        return False

    if os.path.exists(target):
        archive(target)

    os.makedirs(
        os.path.dirname(target),
        exist_ok=True,
    )

    bash(r'''
        ln -sfvrn \
            "{0}" \
            "{1}"

    '''.format(
        source,
        target,
    ))

    return True


def copy_data_dir_simpler(source_dir, target_dir):

    source_dir = os.path.abspath(source_dir)
    target_dir = os.path.abspath(target_dir)

    if not os.path.exists(source_dir):
        return False

    if not os.path.isdir(source_dir):
        return False

    recreate(target_dir)

    for entry in glob.glob(source_dir + os.sep + "*"):
        if os.path.isfile(entry):
            shutil.copy(entry, target_dir)

    logger.info('COPIED (1st-level files): {} --copied-1st-lvl-files--> {}'.format(source_dir, target_dir))


    return True



# ==================================================
#               PATH MANIPULATIONS
# ==================================================
def slugify_filename(file):
    dirname, basename = os.path.split(file)
    filename, extname = os.path.splitext(basename)
    return os.path.join(dirname, slugify_v2(filename) + extname)


def slugify_uniquify_basename(basename):
    filename, extname = os.path.splitext(basename)
    return slugify_v2(filename) + '.{}'.format(uuid.uuid4().hex[:6]) + extname


def slugify_uniquify_filename(file):
    dirname, basename = os.path.split(file)
    return os.path.join(dirname, slugify_uniquify_basename(basename))


def split_path_3_parts(path):
    dirname, basename = os.path.split(path)
    filename, extension = os.path.splitext(basename)
    return dirname, filename, extension



# ==================================================
#                    ITERABLES
# ==================================================
def sliced_dict(Inp_Dict:dict, beg_key=None, end_key=None):

    Out_Dict = {}

    to_beg_slicing = False
    to_end_slicing = False

    if not beg_key:
        to_beg_slicing = True

    for k, Value in Inp_Dict.items():

        if k == end_key:    to_end_slicing = True
        if to_end_slicing:  break

        if to_beg_slicing:  Out_Dict[k] = Value
        if k == beg_key:    to_beg_slicing = True


    if not end_key:
        to_end_slicing = True

    if  not to_beg_slicing \
        or not to_end_slicing :
            raise Exception('Invalid slice: Inp_Dict[{}:{}]'.format(beg_key, end_key))

    return Out_Dict


def pruned_dict(Inp_Dict:dict, Keys_To_Keep:list, strict=False):

    Out_Dict = {}
    if strict:
        for key in Keys_To_Keep:
            Out_Dict[key] = Inp_Dict[key]

    else:
        for key in Keys_To_Keep:
            try:
                Out_Dict[key] = Inp_Dict[key]
            except:
                pass

    return Out_Dict


def sorted_dict(Inp_Dict:dict):
    return dict(sorted(Inp_Dict.items()))


def sorted_dict_by_value(Inp_Dict:dict):
    return dict(sorted(Inp_Dict.items(), key=lambda x: x[1]))


def duration_to_num_frames(duration, frame_shift=0.010, frame_overlap=0.015):
    return int((duration - frame_overlap) / frame_shift)


def split_by_length(total_length, split_length, keep_residual=False):
    Splits = []
    beg = 0
    while beg+split_length-1 <= total_length-1:
        Splits.append([beg, beg+split_length-1])
        beg += split_length
    else:
        if keep_residual:
            Splits.append([beg, total_length-1])
    return Splits


def get_rounded_iterable(Var, decimals=4):

    if type(Var) is list:
        for i in range(len(Var)):
            Var[i] = get_rounded(Var[i], decimals)

    if type(Var) is dict:
        for key, Value in Var.items():
            Var[key] = get_rounded(Value, decimals)

    if type(Var) is float:
        return round(Var, decimals)
    else:
        return Var



# ==================================================
#                    MISCS
# ==================================================
def mktemp(script_path):
    temp_dir = bash('mktemp -d /tmp/{}.XXXX'.format(
        split_path_3_parts(script_path)[1]
    ), strip=True)[0]

    return temp_dir

#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# common
import os
import json


# logger
from .logger import getLogger
logger = getLogger(__name__)


# get_line_count
from .easy_basher import get_line_count


# archive
from .common import archive


def file_to_list(file):

    List = []

    line_count_total = get_line_count(file)

    with open(file, 'r') as f:

        line = f.readline()

        line_count = 1
        while line:

            item = line.split()

            if len(line.split()) == 1:
                List.append(line.split()[0])
            else:
                List.append(line.split())

            line = f.readline()

    return List


def key2value_content_to_dict(key2value_content):

    Key_Value_List = [
        line.split()
        for line in key2value_content.strip().split('\n')
            if line
    ]

    Key2Value = {}

    for key, value in Key_Value_List:
        Key2Value[key] = value

    return Key2Value


def key2values_file_to_dict(key2values_file):

    Key2Values = {}

    line_count_total = get_line_count(key2values_file)

    with open(key2values_file, 'r') as f:

        line = f.readline()

        while line:

            # infs
            key = line.split()[0]
            Values = line.split()[1:]

            Key2Values[key] = Values

            line = f.readline()

    logger.normal('Read {} lines:'.format(line_count_total), key2values_file)

    return Key2Values


def key2value_file_to_dict(key2value_file):

    Key2Values = key2values_file_to_dict(key2value_file)

    for key, Values in Key2Values.items():
            Key2Values[key] = ' '.join(Values)

    return Key2Values # Key2Value


def Key2Value_to_Value2Key(Key2Value:dict):

    Value2Key = {}
    for key, Value in Key2Value.items():
        Value2Key[Value] = key

    return Value2Key


def get_key2value_with_keys_replaced(Key2Value, Key2New_Key):

    New_Key2Value = {}
    for key, Value in Key2Value.items():
        new_key = Key2New_Key[key]
        New_Key2Value[new_key] = Value

    return New_Key2Value


def mapped_2_Key2Value(Key2Value1:dict, Key2Value2:dict):

    is_mismatched = False
    Value1_2_Value2 = {}
    for key in Key2Value1.keys():
        if key in Key2Value2:
            Value1_2_Value2[Key2Value1[key]] = Key2Value2[key]
        else:
            is_mismatched = True

    if is_mismatched:
        logger.warning('Some keys are not matched') # naive check

    return Value1_2_Value2


def write_key2value_to_file(Key2Value, key2value_file, mode='w+', delimiter=' ', to_archive=True):

    if mode.count('w') > 0 and to_archive:
        archive(key2value_file)

    with open(key2value_file, mode) as f:
        for key, Value in Key2Value.items():
            f.write('{} {}\n'.format(
                key,
                delimiter.join(map(str, Value if isinstance(Value, list) else [Value]))
            ))


def write_list_to_file(List, list_file, mode='w+', delimiter=' ', to_archive=True):

    if mode.count('w') > 0 and to_archive:
        archive(list_file)

    with open(list_file, mode) as f:
        for item in List:
            f.write(delimiter.join(map(str, item if isinstance(item, list) else [item]))+'\n')


def write_dict_to_file(Dict, dict_file, mode='w+', to_archive=True):

    if mode.count('w') > 0 and to_archive:
        archive(dict_file)

    with open(dict_file, mode) as f:
        f.write(
            json.dumps(
                Dict,
                indent=4,
                default=str,
                ensure_ascii=False,
            )
        )


def write_str_to_file(Str, str_file, mode='w+', to_archive=True):

    if mode.count('w') > 0 and to_archive:
        archive(str_file)

    with open(str_file, mode) as f:
        f.write(Str)

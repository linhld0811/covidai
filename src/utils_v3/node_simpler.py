#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# common
import os
import time
import traceback


# technical
import glob
import json
import re
import shutil


# logger
from .logger import getLogger
logger = getLogger(__name__)


# file_or_dir
from .inspecter import (

    file_or_dir,
    get_mime_type,
    get_node_size,
)


# common
from .common import (

    get_modified_epoch_time,
    get_timestamp,
    slugify_filename,
)



class NodeHelperSimpler():

    def __init__(
        self,
        write_tracker_file_mode='w+',
        pattern_str__tracker_nodes=r'(^.*)\.(__[a-zA-Z0-9]+__$)',
        size_check_period=1,
        size_check_count_max=6,
        size_waitncheck_backoff_factor=0.5,
        size_waitncheck_count_max=6,
    ):

        self.write_tracker_file_mode = write_tracker_file_mode
        self.pattern_str__tracker_nodes = pattern_str__tracker_nodes
        self.size_check_period = size_check_period
        self.size_waitncheck_backoff_factor = size_waitncheck_backoff_factor
        self.size_check_count_max = size_check_count_max
        self.size_waitncheck_count_max = size_waitncheck_count_max

        self.Regex__Tracker_Nodes = re.compile(pattern_str__tracker_nodes)


    def glob_multi_pattterns(self, Patterns):

        Globbed = []
        for p in Patterns:
            Globbed += glob.glob(p)

        return Globbed


    def get_Nodes_Analysis(self, Node_Patterns, Allowed_Types=('file','dir'), detect_overwrites=False):

        # stage 0
        Nodes_Analysis = {

            'All' : self.glob_multi_pattterns( Node_Patterns ),

            'Non_Trackers' : {

                'All'       : [], # type(self) in Allowed_Types
                'Untracked' : [], # type(self) in Allowed_Types
                'Tracked'   : [], # type(self) in Allowed_Types
            },

            'Trackers' : {
                # '__failed__' : []
                # '__decoded__' : []
                # ...
            },
        }


        # stage 1
        for node in Nodes_Analysis['All']:

            Matching__Tracker = self.Regex__Tracker_Nodes.match(node)

            if not Matching__Tracker:
                if file_or_dir(node) in Allowed_Types:
                    Nodes_Analysis['Non_Trackers']['All'].append(node)

            elif Matching__Tracker:

                tracked_node = Matching__Tracker.group(1)

                if file_or_dir(tracked_node) in Allowed_Types:

                    tracker_file = Matching__Tracker.group(0)
                    tracker_type = Matching__Tracker.group(2)

                    try:
                        Nodes_Analysis['Trackers'][tracker_type].append(tracker_file)
                    except KeyError:
                        Nodes_Analysis['Trackers'][tracker_type] = []
                        Nodes_Analysis['Trackers'][tracker_type].append(tracker_file)

                    Nodes_Analysis['Non_Trackers']['Tracked'].append(tracked_node)


        # stage 2
        Nodes_Analysis['Non_Trackers']['Untracked'] = list(
            set(Nodes_Analysis['Non_Trackers']['All']) - \
            set(Nodes_Analysis['Non_Trackers']['Tracked'])
        )


        # stage 3
        if detect_overwrites:
            for node in Nodes_Analysis['Non_Trackers']['Tracked']:
                node__epoch_modified = get_modified_epoch_time(node)

                for tracker_file in glob.glob(node + '.*'):
                    if get_modified_epoch_time(tracker_file) < node__epoch_modified:
                        logger.warning('Detected overwritten node:', node)
                        self.remove_tracker_files(tracked_node=node)


        return Nodes_Analysis


    def is_busy(self, node):

        prev_size = -1
        for i in range(self.size_check_count_max):
            time.sleep(self.size_check_period)

            try:
                size = get_node_size(node)
                if size == prev_size: return False

            except Exception as e:
                logger.warning(type(e).__name__, e)

            prev_size = size

        return True


    def wait_till_not_busy(self, node):

        count = 0
        while self.is_busy(node):
            if count > self.size_waitncheck_count_max:
                raise Exception('Cant get free :{}'.format(node))
            time.sleep(self.size_waitncheck_backoff_factor)
            count += 1


    def remove_tracker_files(self, tracked_node):

        for inp_node in glob.glob(tracked_node + '.*'):
            Matching__Tracker = self.Regex__Tracker_Nodes.match(inp_node)
            if Matching__Tracker:
                os.remove(inp_node)


    def remove_tracker_files_excluding(self, tracked_node, Excluded_Nodes):

        for inp_node in glob.glob(tracked_node + '.*'):
            Matching__Tracker = self.Regex__Tracker_Nodes.match(inp_node)
            if inp_node not in Excluded_Nodes and Matching__Tracker:
                os.remove(inp_node)


    def write_dict_to_tracker_file(
        self,
        Dict:dict,
        tracked_node,
        status,
        logger_func='green',
    ):

        # stage 0
        tracker_file = tracked_node + '.__{}__'.format(status)
        satus_file__Writer = open(tracker_file, self.write_tracker_file_mode)


        # stage 1
        self.remove_tracker_files_excluding(tracked_node, [tracker_file])


        # stage 2
        satus_file__Writer.write(
            json.dumps(Dict, ensure_ascii=False, indent=4)
        )

        satus_file__Writer.close()


        # stage 3
        try:
            colored_logger = getattr(logger, logger_func)

        except Exception as e:
            logger.warning(type(e).__name__, e)
            colored_logger = logger.blue

        colored_logger('__{}__ :'.format(status), tracker_file)


    def fixnamed(self, inp_node):
        status = 'fixnamed'
        try:

            # stage 0
            out_node = slugify_filename(inp_node)
            if out_node == inp_node:
                return inp_node


            # stage 1
            mimetype = get_mime_type(inp_node)
            logger.warning('Renaming ({}):'.format(mimetype), inp_node)

            if os.path.isfile(inp_node):

                if not os.path.isfile(out_node):
                    shutil.copyfile(
                        inp_node,
                        out_node,
                    )
                else:
                    logger.warning('--> pre-existed', out_node)

            elif os.path.isdir(inp_node):

                if  not os.path.islink(out_node):
                    os.symlink(
                        inp_node,
                        out_node,
                    )
                else:
                    logger.warning('--> pre-existed', out_node)


            # stage 2
            self.write_dict_to_tracker_file(
                {
                    'timestamp' : get_timestamp(),
                    'inp_node'  : inp_node,
                    'out_node'  : out_node,
                },
                inp_node,
                status,
            )


            # stage 3
            return out_node


        except Exception as e:

            self.write_dict_to_tracker_file(
                {
                    'timestamp' : get_timestamp(),
                    'inp_node'  : inp_node,
                    'traceback' : traceback.format_exc(),
                },
                inp_node,
                'failed',
                logger_func='error',
            )

            logger.error(e)
            raise e

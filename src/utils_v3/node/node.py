#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# common
import os, sys
import time
import traceback


# technical
import glob
import json
import mimetypes
import re
import shutil


# node_simpler
from ..node_simpler import NodeHelperSimpler


# converter
from moviepy.editor import *
import codecs
codecs.register_error("strict", codecs.ignore_errors) # hotfix


# logger
from ..logger import getLogger
logger = getLogger(__name__)


# bash
from ..easy_basher import bash


# inspecter
from ..inspecter import (

    get_dur_by_ffmpeg,
    get_mime_type,
)

from ..common import (

    get_timestamp,
)



def try_get_dur(inp_node):

    try:
        dur = None
        dur = get_dur_by_ffmpeg(inp_node)
    except:
        pass

    return dur


class NodeHelper(NodeHelperSimpler):

    def __init__(
        self,

        # from NodeHelperSimpler
        write_tracker_file_mode='w+',
        pattern_str__tracker_nodes=r'(^.*)\.(__[a-zA-Z0-9]+__$)',
        size_check_period=1,
        size_check_count_max=6,

        # mime types
        desired_mime_type_audio='audio/x-wav',
        desired_mime_type_video='video/mp4',

        # audio
        channels=1,
        precision=16,
        sample_rate=16000,
    ):

        # from NodeHelperSimpler
        self.write_tracker_file_mode = write_tracker_file_mode
        self.pattern_str__tracker_nodes = pattern_str__tracker_nodes
        self.size_check_period = size_check_period
        self.size_check_count_max = size_check_count_max

        self.Regex__Tracker_Nodes = re.compile(pattern_str__tracker_nodes)


        # mime types
        self.desired_mime_type_audio = desired_mime_type_audio
        self.desired_mime_type_video = desired_mime_type_video


        self.Desired_MIME_Main_Type_List = [
            'audio',
            'video',
        ]

        self.Desired_MIME_Dict = {
            'audio' : desired_mime_type_audio,
            'video' : desired_mime_type_video,
        }

        self.Desired_MIME_List = [
            desired_mime_type_audio,
            desired_mime_type_video
        ]


        # audio
        self.channels    = int(channels)
        self.precision   = int(precision)
        self.sample_rate = int(sample_rate)

        self.Soxi_Table = [
            [ r'soxi -c {0}', self.channels,    ],
            [ r'soxi -b {0}', self.precision,   ],
            [ r'soxi -r {0}', self.sample_rate, ],
        ]


    def repaired(self, inp_node):
        status = 'repaired'
        try:

            # stage 0
            mime_type = get_mime_type(inp_node)
            if  mime_type.split('/')[0] in self.Desired_MIME_Main_Type_List and try_get_dur(inp_node):
                return inp_node


            # stage 1
            logger.warning('Reparing ({}):'.format(mime_type), inp_node)

            out_node = inp_node+'.repaired'+os.path.splitext(inp_node)[-1]

            if not os.path.isfile(out_node):

                inp_node__replica = inp_node[:]
                out_node__tmp = inp_node+'.repaired.tmp'+os.path.splitext(inp_node)[-1]

                # if  mime_type == 'application/octet-stream':
                if  True:

                    logger.warning('Handling {}'.format(mime_type))

                    bash(
                        r'ffmpeg -i {0} -vn -codec:a copy -map_metadata -1 {1}'.format(
                            inp_node__replica,
                            out_node__tmp
                        )
                    )

                    shutil.move(
                        out_node__tmp,
                        out_node,
                    )

                    inp_node__replica = out_node[:]
                    mime_type = get_mime_type(inp_node__replica)


                if  mime_type == 'video/mp4' and \
                    not try_get_dur(inp_node__replica):

                    logger.warning('Handling {}'.format(mime_type))

                    bash(
                        r'qtfaststart "{0}" "{1}"'.format(
                            inp_node__replica,
                            out_node__tmp,
                        )
                    )

                    shutil.move(
                        out_node__tmp,
                        out_node,
                    )

                    # inp_node__replica = out_node[:]
                    # mime_type = get_mime_type(inp_node__replica)


                if  not os.path.isfile(out_node):
                    raise Exception('Cant repair {}'.format(inp_node))


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


    def converted(self, inp_node):
        status = 'converted'
        try:

            # stage 0
            mime_type = get_mime_type(inp_node)
            if mime_type in self.Desired_MIME_List:
                return inp_node

            # stage 1
            logger.warning('Converting ({}):'.format(mime_type), inp_node)
            mime_type_maintype, _ = mime_type.split('/')

            out_node = r'{0}{1}'.format(
                os.path.splitext(inp_node)[0],
                mimetypes.guess_extension(
                    self.Desired_MIME_Dict[mime_type_maintype]
                )
            )

            if not os.path.isfile(out_node):
                if \
                    mime_type_maintype == 'audio':

                    f = AudioFileClip(
                        inp_node
                    )
                    f.write_audiofile(
                        out_node
                    )

                elif \
                    mime_type_maintype == 'video':

                    f = VideoFileClip(
                        inp_node
                    )
                    f.write_videofile(
                        out_node
                    )
                else:
                    raise Exception('Unsupported maintype: {}'.format(mime_type_maintype))

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


    def audiofied(self, inp_node):
        status = 'audiofied'
        try:

            # stage 0
            mime_type = get_mime_type(inp_node)
            if mime_type == self.desired_mime_type_audio:
                return inp_node


            # stage 1
            logger.warning('Audiofying ({}):'.format(mime_type), inp_node)

            out_node = r'{0}{1}'.format(
                os.path.splitext(inp_node)[0],
                mimetypes.guess_extension(
                    self.Desired_MIME_Dict['audio']
                )
            )

            if not os.path.isfile(out_node):

                f = AudioFileClip(
                    inp_node
                )
                f.write_audiofile(
                    out_node
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


    def resampled(self, inp_node):
        status = 'resampled'
        try:

            # stage 0
            dirname, basename = os.path.split(inp_node)

            to_resample = False
            for Row in self.Soxi_Table:
                spec = bash( Row[0].format(inp_node) )[0]
                spec = int(spec)

                if spec != Row[1]:
                    logger.warning('Mismatched ({} vs {})'.format(spec, Row[1]))
                    to_resample = True
                    break

            if not to_resample:
                return inp_node


            # stage 1
            logger.warning('Resampling:', inp_node)
            out_node \
                = inp_node+'.resampled-'+str(self.sample_rate)+os.path.splitext(inp_node)[-1]

            if not os.path.isfile(out_node):
                bash(r'''
                    sox "{0}" -c {1} -b {2} -r {3} "{4}"
                '''.format(
                        inp_node,
                        self.channels,
                        self.precision,
                        self.sample_rate,
                        out_node,
                ))

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


    def finalized(self, inp_node):
        status = 'finalized'
        try:

            # stage 0-1
            out_node = inp_node


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


    def vetted(self, node):

        if os.path.isdir(node):
            node = self.fixnamed(node)
            node = self.finalized(node)

        if os.path.isfile(node):
            node = self.fixnamed(node)
            node = self.repaired(node)
            node = self.converted(node)
            node = self.audiofied(node)
            node = self.resampled(node)
            node = self.finalized(node)

        return node

    def vetted_verbose(self, node):

        if os.path.isdir(node):
            Node_Vetting = {}           ; Node_Vetting['0rigin']    = node
            node = self.fixnamed(node)  ; Node_Vetting['fixnamed']  = node
            node = self.finalized(node) ; Node_Vetting['finalized'] = node

        if os.path.isfile(node):
            Node_Vetting = {}           ; Node_Vetting['0rigin']    = node
            node = self.fixnamed(node)  ; Node_Vetting['fixnamed']  = node
            node = self.repaired(node)  ; Node_Vetting['repaired']  = node
            node = self.converted(node) ; Node_Vetting['converted'] = node
            node = self.audiofied(node) ; Node_Vetting['audiofied'] = node
            node = self.resampled(node) ; Node_Vetting['resampled'] = node
            node = self.finalized(node) ; Node_Vetting['finalized'] = node

        return node, Node_Vetting

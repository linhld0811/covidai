#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# common
import os


# logger
from ..logger import getLogger
logger = getLogger(__name__)


# get_line_count
from ..easy_basher import get_line_count



def rttm_to_dict(rttm_file):

    RTTM = {}

    line_count_total = get_line_count(rttm_file)

    with open(rttm_file, 'r') as f:

        line = f.readline()
        while line:

            # infs
            reco     = line.split()[1]
            beg_str  = line.split()[3]
            dur_str  = line.split()[4]
            real_spk = line.split()[7]

            # ops
            if reco not in RTTM.keys():
                RTTM[reco] = []

            RTTM[reco].append([beg_str, dur_str, real_spk])

            line = f.readline()

    logger.green('Read {0} lines'.format(line_count_total))

    return RTTM


def write_rttm_to_file(RTTM, rttm_file, rttm_channel=0, mode='w+', archive=True):

    if mode.count('w') > 0 and archive:
        archive(rttm_file)

    with open(rttm_file, mode) as f:
        for reco in RTTM.keys():
            for beg_str, dur_str, real_spk in RTTM[reco]:
                f.write('SPEAKER {0} {1} {2} {3} <NA> <NA> {4} <NA> <NA>\n'.format(
                    reco,
                    rttm_channel,
                    beg_str,
                    dur_str,
                    real_spk,
                ))

    logger.normal('written to {}'.format(rttm_file))


def load_pickled_data_from_scp(scp_file):

    Data = key2value_file_to_dict(scp_file)

    for key in Data.keys():

        # infs
        pickle_file = Data[key]

        # replace file path with actual data
        with open(pickle_file, 'rb') as pickle_reader:
            Data[key] = pickle.load(pickle_reader)

    return Data


def segments_to_spk2utt(Segments):

    Spk2Utt = {}

    for utt, Value in Segments.items():
        spk, beg, end = Value
        if spk not in Spk2Utt:
            Spk2Utt[spk] = []
        Spk2Utt[spk].append(utt)

    for spk in Spk2Utt.keys():
        Spk2Utt[spk].sort()

    return Spk2Utt


def get_utt_id(reco_id, beg_time, end_time, decimals=3, leadings=10):

    utt_id = '{0}-{1}-{2}'.format(
        reco_id,
        str(int(beg_time*(10**decimals))).zfill(leadings),
        str(int(end_time*(10**decimals))).zfill(leadings),
    )

    return utt_id

#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# bash
from ..easy_basher import bash


# get_dur_by_sox
from ..inspecter import get_dur_by_sox



def remove_empty_timeslices(Timeslices):

    New_Timeslices = []
    for timslice in Timeslices:
        if timslice[1] - timslice[0] > 0:
            New_Timeslices.append(timslice)

    return New_Timeslices


def get_Anti_Timeslices(Timeslices, total_duration):

    # stage 0
    Anti_Timeslices = []


    # stage 1
    Anti_Timeslices.append(
        [0, Timeslices[0][0]]
    )


    # stage 2
    for i in range(len(Timeslices))[0:-1]:

        beg = Timeslices[i  ][1]
        end = Timeslices[i+1][0]

        Anti_Timeslices.append([beg, end])


    # stage 3
    Anti_Timeslices.append(
        [Timeslices[-1][-1], total_duration]
    )


    # stage 4
    Anti_Timeslices = remove_empty_timeslices(Anti_Timeslices)


    return Anti_Timeslices


def get_SNR(wav_file, Timeslices, max_SNR=10000):

    Anti_Timeslices = get_Anti_Timeslices(
        Timeslices,
        get_dur_by_sox(wav_file)
    )

    RMS_amplitude__Timeslices      = get_RMS_amplitude_by_sox(wav_file, Timeslices)
    RMS_amplitude__Anti_Timeslices = get_RMS_amplitude_by_sox(wav_file, Anti_Timeslices)

    if RMS_amplitude__Anti_Timeslices == 0:
        return max_SNR

    SNR = RMS_amplitude__Timeslices / RMS_amplitude__Anti_Timeslices

    return SNR


def get_RMS_amplitude_by_sox(wav_file, Timeslices):

    cmd = ''

    for segment in Timeslices:
        cmd += '={} ={} \\\n'.format(
            segment[0],
            segment[1],
        )

    cmd = 'sox {} -n trim '.format(wav_file) + cmd + ' stat'
    cmd += ' 2>&1 | grep amplitude | grep RMS | awk \'{print $3}\''

    RMS_amplitude = float(bash(cmd, silent=True)[0])

    return RMS_amplitude

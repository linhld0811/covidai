#!/usr/bin/env python3

# Copyright 2010 Iowa State University (author: Forrest Bao)
#           2011 (author: alevchuk)
#           2020 (author: lamnt45)


# technical
import string


# logger
from ..logger import getLogger
logger = getLogger(__name__)


# pandas
pd = None
try:
    import pandas as pd
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)
except Exception as e:
    logger.warning('{}'.format(e))
    pass


# envs
EMPTY_MARK_STR=''
match_award      = 20
mismatch_penalty = -5
gap_penalty      = -5 # both for opening and extanding


def zeros(shape):
    "Re-implementation of numpy.zeros"

    retval = []
    for x in range(shape[0]):
        retval.append([])
        for y in range(shape[1]):
            retval[-1].append(0)
    return retval


def match_score(alpha, beta):
    if alpha == beta:
        return match_award
    elif alpha == EMPTY_MARK_STR or beta == EMPTY_MARK_STR:
        return gap_penalty
    else:
        return mismatch_penalty

def finalize(align1, align2):
    align1.reverse()    #reverse sequence 1
    align2.reverse()    #reverse sequence 2

    i,j = 0,0

    #calcuate identity, score and aligned sequeces

    found = 0
    score = 0
    identity = 0
    for i in range(0,len(align1)):
        # if two AAs are the same, then output the letter
        if align1[i] == align2[i]:

            identity = identity + 1
            score += match_score(align1[i], align2[i])

        # if they are not identical and none of them is gap
        elif align1[i] != align2[i] and align1[i] != EMPTY_MARK_STR and align2[i] != EMPTY_MARK_STR:
            score += match_score(align1[i], align2[i])
            found = 0

        #if one of them is a gap, output a space
        elif align1[i] == EMPTY_MARK_STR or align2[i] == EMPTY_MARK_STR:
            score += gap_penalty

    identity = float(identity) / len(align1)

    return identity, score, align1, align2


def needle(seq1, seq2):
    m, n = len(seq1), len(seq2)  # length of two sequences

    # Generate DP table and traceback path pointer matrix
    score = zeros((m+1, n+1))      # the DP table

    # Calculate DP table
    for i in range(0, m + 1):
        score[i][0] = gap_penalty * i
    for j in range(0, n + 1):
        score[0][j] = gap_penalty * j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            match = score[i - 1][j - 1] + match_score(seq1[i-1], seq2[j-1])
            delete = score[i - 1][j] + gap_penalty
            insert = score[i][j - 1] + gap_penalty
            score[i][j] = max(match, delete, insert)

    # Traceback and compute the alignment
    align1, align2 = [], []
    i,j = m,n # start from the bottom right cell
    while i > 0 and j > 0: # end toching the top or the left edge
        score_current = score[i][j]
        score_diagonal = score[i-1][j-1]
        score_up = score[i][j-1]
        score_left = score[i-1][j]

        if score_current == score_diagonal + match_score(seq1[i-1], seq2[j-1]):
            align1.append(seq1[i-1])
            align2.append(seq2[j-1])
            i -= 1
            j -= 1
        elif score_current == score_left + gap_penalty:
            align1.append(seq1[i-1])
            align2.append(EMPTY_MARK_STR)
            i -= 1
        elif score_current == score_up + gap_penalty:
            align1.append(EMPTY_MARK_STR)
            align2.append(seq2[j-1])
            j -= 1

    # Finish tracing up to the top left cell
    while i > 0:
        align1.append(seq1[i-1])
        align2.append(EMPTY_MARK_STR)
        i -= 1
    while j > 0:
        align1.append(EMPTY_MARK_STR)
        align2.append(seq2[j-1])
        j -= 1

    return finalize(align1, align2)


def water(seq1, seq2):
    m, n = len(seq1), len(seq2)  # length of two sequences

    # Generate DP table and traceback path pointer matrix
    score = zeros((m+1, n+1))      # the DP table
    pointer = zeros((m+1, n+1))    # to store the traceback path

    max_score = 0        # initial maximum score in DP table
    # Calculate DP table and mark pointers
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            score_diagonal = score[i-1][j-1] + match_score(seq1[i-1], seq2[j-1])
            score_up = score[i][j-1] + gap_penalty
            score_left = score[i-1][j] + gap_penalty
            score[i][j] = max(0,score_left, score_up, score_diagonal)
            if score[i][j] == 0:
                pointer[i][j] = 0 # 0 means end of the path
            if score[i][j] == score_left:
                pointer[i][j] = 1 # 1 means trace up
            if score[i][j] == score_up:
                pointer[i][j] = 2 # 2 means trace left
            if score[i][j] == score_diagonal:
                pointer[i][j] = 3 # 3 means trace diagonal
            if score[i][j] >= max_score:
                max_i = i
                max_j = j
                max_score = score[i][j]

    align1, align2 = [], []    # initial sequences

    i,j = max_i,max_j    # indices of path starting point

    #traceback, follow pointers
    while pointer[i][j] != 0:
        if pointer[i][j] == 3:
            align1.append(seq1[i-1])
            align2.append(seq2[j-1])
            i -= 1
            j -= 1
        elif pointer[i][j] == 2:
            align1.append(EMPTY_MARK_STR)
            align2.append(seq2[j-1])
            j -= 1
        elif pointer[i][j] == 1:
            align1.append(seq1[i-1])
            align2.append(EMPTY_MARK_STR)
            i -= 1

    return finalize(align1, align2)


def add_space_around_punctuation_marks(src__str):

    # stage 0
    if not src__str:
        return src__str

    # stage 1
    tgt__str = ''
    for i in range(len(src__str)-1):
        if src__str[i] in string.punctuation and src__str[i+1] == ' ':
            tgt__str += ' ' + src__str[i]
        else:
            tgt__str += src__str[i]

    # stage 2
    if src__str[-1] in string.punctuation:
        tgt__str += ' ' + src__str[-1]
    else:
        tgt__str += src__str[-1]

    return tgt__str


def align_text2text_with_confidences(Src__Words_n_Confidences, Tgt, marking_confidence=1.0, god_mode=False, verbose=True):

    # stage -1
    if not verbose: logger_green = logger.nothing
    else:           logger_green = logger.green


    # stage 0
    logger_green('Performing Smith-Waterman Text2Text alignments')

    Src = [ x['word'] for x in Src__Words_n_Confidences ]

    if Src == Tgt:
        logger_green('Skipped since Src == Tgt')
        return Src__Words_n_Confidences

    _, _, Src__Aligned, Tgt__Aligned = needle( Src, Tgt )

    if len(Src__Aligned) != len(Tgt__Aligned):
        raise Exception('len(Src__Aligned) != len(Tgt__Aligned)')


    # stage 1
    logger_green('Recovering Src__Aligned__Word_n_Confidence')

    Src__Aligned__Word_n_Confidence = []
    src__confidence_idx = -1
    for i in range(len(Src__Aligned)):

        if Src__Aligned[i]:
            src__confidence_idx += 1
            Src__Aligned__Word_n_Confidence.append({
                'word'       : Src__Words_n_Confidences[src__confidence_idx]['word'],
                'confidence' : Src__Words_n_Confidences[src__confidence_idx]['confidence'],
            })
        else:
            Src__Aligned__Word_n_Confidence.append({
                'word'       : '',
                'confidence' : None,
            })


    # stage 2
    logger_green('Marking..')
    Markers = []
    mark_count =  min(len(Src__Aligned),len(Tgt__Aligned))
    for i in range(mark_count):

        marker = ''

        if Src__Aligned[i] == Tgt__Aligned[i]:
            marker = '___'

        elif not Src__Aligned[i] and Tgt__Aligned[i]:
            marker = 'INS'

        elif Src__Aligned[i] and not Tgt__Aligned[i]:
            marker = 'DEL'

        elif Src__Aligned[i] and Tgt__Aligned[i] and (Src__Aligned[i] != Tgt__Aligned[i]):
            marker = 'SUB'

        Markers.append(marker)


    # stage 3
    logger_green('Clustering.. (linear mode)')

    Clusters = [0,]
    for i in range(1, len(Markers)):
        if ( Markers[i] != Markers[i-1] ) and ( sorted(Markers[i-1:i+1]) != ['DEL', 'SUB'] ):
            Clusters.append(Clusters[i-1] + 1)
        else:
            Clusters.append(Clusters[i-1])

    Cluster2WnC = {} # Cluster 2 Word_n_Confidence (both src and tgt)
    for i in range(len(Markers)):

        if Clusters[i] not in Cluster2WnC.keys():
            Cluster2WnC[Clusters[i]] = []

        Cluster2WnC[Clusters[i]].append(
            {
                'src__aligned' : Src__Aligned[i],
                'src__word'    : Src__Aligned__Word_n_Confidence[i]['word'],
                'tgt__aligned' : Tgt__Aligned[i],
                'marker'       : Markers[i],
                'src__cfd'     : Src__Aligned__Word_n_Confidence[i]['confidence'],
            }
        )


    # stage 4
    logger_green('DEL clusters adjacent to a SUB will be all turned into SUB')
    Cluster2All_Markers = {}
    for key in Cluster2WnC.keys():
        Cluster2All_Markers[key] = set(
            sorted( [x['marker'] for x in Cluster2WnC[key]] )
        )

    for key in Cluster2WnC.keys():
        if Cluster2All_Markers[key] == {'SUB', 'DEL'} :
            for i in range(len(Cluster2WnC[key])) :
                Cluster2WnC[key][i]['marker'] = 'SUB'
            Cluster2All_Markers[key] = {'SUB'}


    # stage 5
    logger_green('Getting words confidences')
    for key in Cluster2WnC.keys():
        if Cluster2All_Markers[key] == {'___'}:
            for i in range(len(Cluster2WnC[key])) :
                Cluster2WnC[key][i]['tgt__cfd'] = Cluster2WnC[key][i]['src__cfd']

        if Cluster2All_Markers[key] == {'DEL'}:
            for i in range(len(Cluster2WnC[key])) :
                Cluster2WnC[key][i]['tgt__cfd'] = None

    if god_mode:
        for key in Cluster2WnC.keys():
            if Cluster2All_Markers[key] in [ {'INS'}, {'SUB'} ]:
                for i in range(len(Cluster2WnC[key])) :
                    Cluster2WnC[key][i]['tgt__cfd'] = 1

    else:
        for key in Cluster2WnC.keys():

            if Cluster2All_Markers[key] == {'INS'}:
                for i in range(len(Cluster2WnC[key])) :
                    Cluster2WnC[key][i]['tgt__cfd'] = marking_confidence

            if Cluster2All_Markers[key] == {'SUB'}:

                Src__Confidences = [m['src__cfd'] for m in Cluster2WnC[key]]
                src__confidences_mean = sum(Src__Confidences) / len(Src__Confidences)

                for i in range(len(Cluster2WnC[key])) :
                    Cluster2WnC[key][i]['tgt__cfd'] = src__confidences_mean * marking_confidence


    # stage 6
    logger_green('De-clustering Cluster2WnC into Word_n_Confidence for logging')

    Word_n_Confidence = []
    for value in Cluster2WnC.values():
        Word_n_Confidence += value

    if pd:
        logger_green(
            'Word_n_Confidence (Data Frames):\n',
            pd.DataFrame(Word_n_Confidence),
        )


    # stage 7
    logger_green('Getting Tgt__Words_n_Confidences')
    Tgt__Words_n_Confidences = []
    for x in Word_n_Confidence:

        if x['tgt__aligned']:
            Tgt__Words_n_Confidences.append(
                {
                    'word'       : x['tgt__aligned'],
                    'confidence' : x['tgt__cfd'],
                }
            )

    return Tgt__Words_n_Confidences


if __name__ == '__main__':

    # Src_Text = r'nếu muốn nợ tiền hoặc vay tiền để anh có hai con nhà chị nó sẽ có thể muốn gì nữa cộng thêm vào cuộc cách mạng ấy cộng tác viên là các doanh nghiệp có mệnh giá theo cái chủ nghĩa đã hết em không khí trên xe vẫn là năm phần trăm tổng thu nhập do hai bảy không bốn hai hai nói .'

    Src__Words_n_Confidences = [{'word': 'nếu', 'confidence': 0.6408}, {'word': 'muốn', 'confidence': 0.5968}, {'word': 'nợ', 'confidence': 0.735}, {'word': 'tiền', 'confidence': 0.3811}, {'word': 'hoặc', 'confidence': 0.6853}, {'word': 'vay', 'confidence': 0.6823}, {'word': 'tiền', 'confidence': 0.935}, {'word': 'để', 'confidence': 0.6228}, {'word': 'anh', 'confidence': 0.6141}, {'word': 'có', 'confidence': 0.9587}, {'word': 'hai', 'confidence': 0.679}, {'word': 'con', 'confidence': 0.2621}, {'word': 'nhà', 'confidence': 0.1338}, {'word': 'chị', 'confidence': 0.1396}, {'word': 'nó', 'confidence': 0.3972}, {'word': 'sẽ', 'confidence': 0.517}, {'word': 'có', 'confidence': 0.3788}, {'word': 'thể', 'confidence': 0.6169}, {'word': 'muốn', 'confidence': 0.8353}, {'word': 'gì', 'confidence': 0.5157}, {'word': 'nữa', 'confidence': 0.4353}, {'word': 'cộng', 'confidence': 0.5408}, {'word': 'thêm', 'confidence': 0.2403}, {'word': 'vào', 'confidence': 0.406}, {'word': 'cuộc', 'confidence': 0.3368}, {'word': 'cách', 'confidence': 0.154}, {'word': 'mạng', 'confidence': 0.5179}, {'word': 'ấy', 'confidence': 0.5502}, {'word': 'cộng', 'confidence': 0.0502}, {'word': 'tác', 'confidence': 0.317}, {'word': 'viên', 'confidence': 0.5003}, {'word': 'là', 'confidence': 0.5936}, {'word': 'các', 'confidence': 0.8113}, {'word': 'doanh', 'confidence': 0.8848}, {'word': 'nghiệp', 'confidence': 0.8953}, {'word': 'có', 'confidence': 0.8218}, {'word': 'mệnh', 'confidence': 0.1902}, {'word': 'giá', 'confidence': 0.2857}, {'word': 'theo', 'confidence': 0.4777}, {'word': 'cái', 'confidence': 0.462}, {'word': 'chủ', 'confidence': 0.4133}, {'word': 'nghĩa', 'confidence': 0.7629}, {'word': 'đã', 'confidence': 0.7047}, {'word': 'hết', 'confidence': 0.0726}, {'word': 'em', 'confidence': 0.4622}, {'word': 'không', 'confidence': 0.1383}, {'word': 'khí', 'confidence': 0.8713}, {'word': 'trên', 'confidence': 0.7002}, {'word': 'xe', 'confidence': 0.5082}, {'word': 'vẫn', 'confidence': 0.7828}, {'word': 'là', 'confidence': 0.4623}, {'word': 'năm', 'confidence': 0.5002}, {'word': 'phần', 'confidence': 0.9258}, {'word': 'trăm', 'confidence': 0.755}, {'word': 'tổng', 'confidence': 0.4463}, {'word': 'thu', 'confidence': 0.845}, {'word': 'nhập', 'confidence': 0.7568}, {'word': 'do', 'confidence': 0.6638}, {'word': 'hai', 'confidence': 0.9651}, {'word': 'bảy', 'confidence': 0.8504}, {'word': 'không', 'confidence': 0.7442}, {'word': 'bốn', 'confidence': 0.4386}, {'word': 'hai', 'confidence': 0.5031}, {'word': 'hai', 'confidence': 0.7146}, {'word': 'nói', 'confidence': 0.5888}, {'word': '.', 'confidence': 0.963}]


    Tgt_Text = r'Nếu muốn nợ tiền hoặc vay tiền để anh có hai con nhà chị nó sẽ có thể muốn gì nữa. Cộng thêm vào cuộc cách mạng ấy, cộng tác viên là các doanh nghiệp có theo cái chủ nghĩa. Đã hết em không khí trên xe vẫn là 5% tổng thu nhập do 27-0422 nói.'

    Tgt = add_space_around_punctuation_marks(Tgt_Text).split()

    align_text2text_with_confidences(Src__Words_n_Confidences, Tgt)
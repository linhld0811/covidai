# common
import os

# subprocess
import subprocess

# local
import config as cf

# utils_v3
import utils_v3
logger = utils_v3.getLogger(__name__)

def convert_rate(src_folder, dst_folder):
    """
    convert and resample (16k) audio from some format(mp3; amr) to .wav
    """
    if not os.path.isdir(src_folder):
        logger.green("Source folder doesn't exist, continue")
    if not os.path.isdir(dst_folder): os.makedirs(dst_folder)

    fns = [fn for fn in os.listdir(src_folder) if
                any(map(fn.endswith, ['.mp3', '.wav', '.amr']))]

    for i, fn in enumerate(fns):
        old_fn = os.path.join(src_folder, fn)
        new_fn = os.path.join(dst_folder, fn)
        if os.path.isfile(new_fn): continue
        # convert all file to wav, mono, sample rate 8000
        subprocess.call(['ffmpeg', '-loglevel', 'panic', '-i',  old_fn,
                '-acodec', 'pcm_s16le', '-ac', '1', '-ar', cf.RATE, new_fn])
        if (i+1)%100 == 0:
            logger.green('{}/{}: {}'.format(i+1, len(fns), new_fn))


if __name__ == '__main__':
    for cate in cf.CATES:
        src_folder = os.path.join(cf.DATA_DIR, cate)
        dst_folder = os.path.join(cf.DATA_DIR, cf.RATE, cate)
        convert_rate(src_folder, dst_folder)



# common
import random
import numpy as np

# scipy
from scipy import signal
from scipy.io import wavfile

# pillow
from PIL import Image

def random_segment(audio_signal, N):
    length = audio_signal.shape[0]
    if N < length:
        start = random.randint(0, length - N)
        audio_signal = audio_signal[start:start + N]
    else:
        tmp = np.zeros((N,))
        start = random.randint(0, N - length)
        tmp[start: start + length] = audio_signal
        audio_signal = tmp
    return audio_signal

def log_specgram(audio, sample_rate, window_size=20, step_size=10, eps=1e-10):
    nperseg = int(round(window_size * sample_rate / 1e3))
    noverlap = int(round(step_size * sample_rate / 1e3))
    freqs, _, spec = signal.spectrogram(audio,
                                        fs=sample_rate,
                                        window='hann', # 'text'
                                        nperseg=nperseg,
                                        noverlap = noverlap,
                                        detrend=False)
    return np.log(spec.T.astype(np.float32) + eps)

def gen_spec(wav_path, duration):
    samplerate, test_sound = wavfile.read(wav_path)
    N = int(duration*samplerate)
    segment_sound = random_segment(test_sound, N)
    spectrogram = log_specgram(segment_sound, samplerate).astype(np.float32)

    # convert to ResNet input
    spectrogram = np.array(Image.fromarray(spectrogram).resize((224, 224), resample = Image.BICUBIC))
    out = np.zeros((3, 224, 224), dtype = np.float32)
    out[0, :, :] = spectrogram
    out[1, :, :] = spectrogram
    out[2, :, :] = spectrogram
    return out
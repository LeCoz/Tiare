__author__ = 'Maxime Le Coz'
import soundfile as sf
from math import sqrt


def load_sound(filepath):
    data, samplerate = sf.read(filepath)
    if len(data.shape) == 2:
        data = data[:, 1]
    print len(data)
    return data, float(samplerate)


def cut(serie, threshold, minlen, minlensil):

    segments = []

    if serie[0] > threshold :
        start = 0
    else:
        start = None

    for i, s in enumerate(serie):

        if start is None and s > threshold:

            if len(segments) > 0 and (i-segments[-1][1]) < minlensil :
                start = segments[-1][0]
                segments = segments[:-1]

            elif len(segments) == 0 and i < minlen:
                start = 0
            else:
                start = i

        if start is not None and s <= threshold:

            if i-start > minlen:

                segments += [(start, i)]

            start = None

    if start is not None:

        segments += [(start, len(serie)-1)]

    return segments


def rms(frame):
    return sqrt(float(sum(map(lambda x: x*x, frame)))/float(len(frame)))


def energy(samples, samplerate, wstep=0.01, wlen=0.01):
    wstep = int(wstep*samplerate)
    wlen = int(wlen*samplerate)
    w = int(wlen/2)
    timeline = range(w, len(samples)-w, wstep)
    energy_values = map(lambda t: rms(samples[t-w:t+w]), timeline)
    em = max(map(abs, energy_values))

    return [float(t)/samplerate for t in timeline],[v/em for v in energy_values]

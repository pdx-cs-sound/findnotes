#!/usr/bin/python3
# Copyright (c) 2019 Bart Massey
# [This program is licensed under the "MIT License"]
# Please see the file LICENSE in the source
# distribution of this software for license terms.

# Find maximum and minimum sample in an audio file.

import array
import math
import numpy as np
import sys
import wave as wav

# Number of cycles to get a decent Goertzel output.
ncycles = 5

# Get the signal file.
with wav.open(sys.argv[1], 'rb') as wavfile:
    global samples, rate

    # Channels per frame.
    channels = wavfile.getnchannels()
    assert channels == 1

    # Bytes per sample.
    width = wavfile.getsampwidth()
    assert width == 2

    # Sample rate
    rate = wavfile.getframerate()

    # Number of frames.
    nframes = wavfile.getnframes()

    # Get the signal.
    wave_bytes = wavfile.readframes(nframes)

    # Unpack the signal.
    samples = np.array(array.array('h', wave_bytes),
                       dtype=np.dtype(np.float)) / 32768.0


# Goertzel Filter
# https://en.wikipedia.org/wiki/Goertzel_algorithm eqn 6
class GoertzelFilter(object):
    def __init__(self, freq, length):
        w = 2 * math.pi * freq / rate
        self.norm = np.exp(np.complex(0, w * length))
        self.coeff = np.array([np.exp(np.complex(0, -w * k))
                               for k in range(length)])
        self.length = length

    def filter(self, samples):
        assert len(samples) == self.length
        return self.norm * np.dot(self.coeff, samples)

# Set up filter bank, output note names.
base_names = ["A", "A#/Bb", "B", "C", "C#/Db", "D", "D#/Eb",
              "E", "F", "F#/Gb", "G", "G#/Ab" ]
assert len(base_names) == 12
note_base = 21
note_filters = []
note_freqs = []
note_names = []
for key in range(note_base, 89):
    freq = 440 * 2**((key - 69) / 12)
    note_freqs.append(freq)

    length = int(ncycles * rate / freq)
    note_filters.append(GoertzelFilter(freq, length))

    note = key - note_base
    name = base_names[note % 12] + "[" + str(note // 12) + "]"
    note_names.append(name)

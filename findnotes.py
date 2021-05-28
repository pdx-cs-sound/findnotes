#!/usr/bin/python3
# Copyright (c) 2019 Bart Massey
# [This program is licensed under the "MIT License"]
# Please see the file LICENSE in the source
# distribution of this software for license terms.

# Find notes in an audio file.

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
        fwindow = np.blackman(length)
        self.coeff = fwindow * np.array([np.exp(np.complex(0, -w * k))
                               for k in range(length)])
        self.length = length


    def filter(self, samples):
        assert len(samples) == self.length
        return self.norm * np.dot(self.coeff, samples)

window_len = int(rate * 0.05)

# Set up filter bank, output note names.
base_names = ["A", "A#/Bb", "B", "C", "C#/Db", "D", "D#/Eb",
              "E", "F", "F#/Gb", "G", "G#/Ab" ]
assert len(base_names) == 12
note_base = 57
note_end = 80
note_filters = []
note_freqs = []
note_names = []
for key in range(note_base, note_end + 1):
    freq = 440 * 2**((key - 69) / 12)
    note_freqs.append(freq)

    note_filters.append(GoertzelFilter(freq, window_len))

    note = key - 9
    name = base_names[note % 12] + "[" + str(note // 12) + "]"
    note_names.append(name)

notes_samples = []
for t in range(0, len(samples) - window_len, window_len):
    window = samples[t:t+window_len]
    powers = [abs(f.filter(window)) for f in note_filters]
    # print(round(t / rate, 2))
    ps = []
    for key in range(note_base, note_end + 1):
        ix = key - note_base
        ps.append(powers[ix])
        # print(f"  {note_names[ix]} {round(powers[ix], 2)}")

    ix, px = max(enumerate(ps), key=lambda p: p[1])
    tx = round(t / rate, 2)
    if px > 50:
        # print(f"{tx} {note_names[ix]} {px}")
        notes_samples.append(ix)
    else:
        # print(f"{tx} rest {px}")
        notes_samples.append(None)

notes = [notes_samples[0]]
for i in range(1, len(notes_samples)):
    if notes_samples[i-1] != notes_samples[i]:
        notes.append(notes_samples[i])

for ix in notes:
    if ix is not None:
        print(note_names[ix])

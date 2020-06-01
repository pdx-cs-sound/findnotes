# Copyright (c) 2018 Bart Massey
# [This program is licensed under the "MIT License"]
# Please see the file LICENSE in the source
# distribution of this software for license terms.

# Solution to CS 410P/510 Sound HW1: Clipped

import argparse, array, math, pyaudio, struct, sys, time, wave

# Parse arguments.
parser = argparse.ArgumentParser()
parser.add_argument(
    "--write",
    help="write to file <tone>.wav",
    action="store_true",
)
parser.add_argument(
    "--freq",
    help="frequency",
    type=int,
    default=440,
)
parser.add_argument(
    "tone",
    help="which tone to play (sine, clipped)",
)
args = parser.parse_args()

# Sample rate in frames per second.
SAMPLE_RATE = 48_000

# Tone max amplitude.
AMPLITUDE = 0.25

# Total output time in seconds.
DURATION = 1.0

# Size of output buffer in frames. Less than 1024 is not
# recommended, as most audio interfaces will choke
# horribly.
BUFFER_SIZE = 2048

# Sine generator generator.
def waveform_sine(nsamples):
    w = 2 * math.pi * args.freq / SAMPLE_RATE
    for t in range(nsamples):
        yield AMPLITUDE * math.sin(t * w)

# Clipped sine generator generator.
def waveform_clipped(nsamples):
    w = 2 * math.pi * args.freq / SAMPLE_RATE
    for t in range(nsamples):
        sine = 2 * AMPLITUDE * math.sin(t * w)
        clip = AMPLITUDE
        yield max(min(sine, clip), -clip)

# Write a tone to a wave file.
def write(wav, filename):
    samples = [int(s * (1 << 15)) for s in wav]
    frames = array.array('h', samples)
    w = wave.open(filename, "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SAMPLE_RATE)
    w.setnframes(len(samples))
    w.writeframesraw(frames)
    w.close()

# Play a tone on the computer.
def play(wav):

    # Set up and start the stream.
    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate = SAMPLE_RATE,
        channels = 1,
        format = pyaudio.paFloat32,
        output = True,
        frames_per_buffer = BUFFER_SIZE,
    )

    # Write the samples.
    done = False
    while not done:
        buffer = list()
        for _ in range(BUFFER_SIZE):
            try:
                sample = next(wav)
            except StopIteration:
                done = True
                break
            buffer.append(sample)
        pbuffer = struct.pack("{}f".format(len(buffer)), *buffer)
        stream.write(pbuffer)

    # Tear down the stream.
    stream.close()


# Get tone generator.
nsamples = int(DURATION * SAMPLE_RATE)
if args.tone == "sine":
    wav = waveform_sine(nsamples)
elif args.tone == "clipped":
    wav = waveform_clipped(nsamples)
else:
    print(f"unknown tone {args.tone}", file=sys.stderr)
    exit(1)

# Write or play the tone.
if args.write:
    write(wav, args.tone + ".wav")
else:
    play(wav)

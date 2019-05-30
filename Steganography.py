import sys
import wave as wav
import struct as st
import numpy as np
import math as mt


wav_file = wav.open(sys.argv[1], 'rb')  # Open the audio file.
wav_channels = wav_file.getnchannels()  # Get total number of channels.
wav_frames = wav_file.getnframes()  # Get total number of frames.
frame_rate = wav_file.getframerate()  # Frame rate.
sample_size = 160  # Frames sample size.
mark_freq = 2225  # Mark frequency.
space_freq = 2025  # Space frequency.

# Read frames as an array of bytes.
wav_bytes = wav_file.readframes(wav_frames)

# Convert frames from bytes to floating point.
wav_floats = st.unpack("%ih" % (wav_frames * wav_channels), wav_bytes)
wav_floats = [float(i) / pow(2, 15) for i in wav_floats]

# Goertzl filer.


def filter(sample, filter_freq):
    target_filter = (2*mt.pi*filter_freq)/frame_rate
    normalize = np.exp(np.complex(0, target_filter*sample_size))
    coef = np.array([np.exp(np.complex(0, -target_filter * i))
                     for i in range(sample_size)])
    return abs(normalize * np.dot(sample, coef))

# Get the FSK bits


def get_FSK():
    bits = []
    # Iterate through the frames by sample size (160 frames/sample)
    for i in range(0, len(wav_floats), sample_size):
        # Get the next sample (160 frames)
        curr_sample = wav_floats[i: i + sample_size]

        # Get the mark/space size
        mark_size = filter(curr_sample, mark_freq)
        space_size = filter(curr_sample, space_freq)

        # Comapre the mark/space size
        if(mark_size > space_size):
            bits.append(1)
        else:
            bits.append(0)
    return bits


def get_message(fsk):
    message = ""
    for i in range(0, len(fsk), 10):
        current_byte = (fsk[i: i+10])[1:9]  # Get the middle 8 bits
        pow = [2 ** j for j in range(8)]  # Get powers of 2 for total bits
        ascii = np.dot(current_byte, pow)  # Get the ascii value
        message += chr(ascii)  # Convert ascii to char
    return message


print(get_message(get_FSK()))  # Print the hidden message

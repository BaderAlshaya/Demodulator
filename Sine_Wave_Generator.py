import sys
import wave
import struct as st
import numpy as np
import scipy as sc

# Example Input:
# Amplitude = 1000
# Frame rate = 48000
# Number of frames = 50000
# Number of channels = 1
# Width = 2
# Play time = 3
# Audio name = cool

# Get audio info
audio_name = str(input("Enter target audio name: ")) + ".wav"
audio_length = int(input("Enter target audio length: "))

# Get sine wave info
amplitude = int(input("Enter amplitude: "))
frequency = float(input("Enter frequency: "))
frame_rate = float(input("Enter frame rate: "))
wav_frames = int(input("Enter number of frames: "))
channels = int(input("Enter number of channels: "))
width = int(input("Enter width: "))

# Generate sine wave data
sine_wave = [np.sin(2 * np.pi * frequency * i / frame_rate)
            for i in range(wav_frames * audio_length)]

# Create .wav audio file for the target sine wave
wav_file = wave.open(audio_name, "w")
wav_file.setparams((channels, width, int(
    frame_rate), wav_frames, "NONE", "NONE"))

# Write the sine wave data into the audio file in hex
for i in sine_wave:
    wav_file.writeframes(st.pack("h", int(i*amplitude)))

# Print the result
print("------------[Gnereated]------------")
print("Audio Name:", audio_name)
print("Audio Length: ", audio_length)
print("-----------------------------------")

import sys
import wave as wav
import struct as st
import numpy as np
import math as mt
import audiolab
import scipy


def get_next_frequency(seedno):
    np.random.seed(seedno)
    if seedno > 7500:
        return np.random.randint(7501, 15000)
    return np.random.randint(1500, 7500)


print("Please choose one of the following options:")
print("1. Encode text into audio file.")
print("2. Decode text from audio file.")
print("3. Hide endoded message in another audio file.")
choice = int(input("Your choice: "))
print("------------------")


###### Encode text message ######
if choice == 1:
  message_str = str(input("Enter text message to encode: "))
  # These will be recalculated after each window for cryptographic security
  seed_mark_int = int(input("Enter the key for the mark frequencies (value between 7501 and 15000): "))
  seed_space_int = int(input("Enter the key for the space frequencies (value between 1500 and 7500): "))

  ##### For Steven, these will be the frequencies use for the first window
  mark_freq = get_next_frequency(seed_mark_int)
  space_freq = get_next_frequency(seed_space_int)

  ##### Use this for each following window
  mark_freq = get_next_frequency(mark_freq)
  space_freq = get_next_frequency(space_freq)

  ##### Since we are using seeds in a PRNG, it will always come up with the same sequence of numbers and can only be decrypted if you know the seed numbers






###### Decode text message ######
elif choice == 2:
  file = str(input("Enter audio path to decode: "))
  seed_mark_int = int(input("Enter the key for the mark frequencies: "))
  seed_space_int = int(input("Enter the key for the space frequencies: "))
  wav_file = wav.open(file, 'rb')  # Open the audio file.
  wav_channels = wav_file.getnchannels()  # Get total number of channels.
  wav_frames = wav_file.getnframes()  # Get total number of frames.
  frame_rate = wav_file.getframerate()  # Frame rate.
  sample_size = int(frame_rate/300)  # Frames sample size.
  mark_freq = seed_mark_int  # Mark frequency.
  space_freq = seed_space_int  # Space frequency.

  print(sample_size)
  print("rate: ", frame_rate)
  print("frames: ", wav_frames)
  print("width: ", wav_file.getsampwidth())
  print("channels: ", wav_channels)

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
          mark_size = filter(curr_sample, get_next_frequency(mark_freq))
          space_size = filter(curr_sample, get_next_frequency(space_freq))

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


elif choice == 3:
    message_to_hide = str(input("Please enter the path of the encoded message to hide: "))
    file_to_hide_in = str(input("Please enter the name of the file to hide the message in: "))
    a, fs, enc = audiolab.wavread(message_to_hide)
    b, fs, enc = audiolab.wavread(file_to_hide_in)
    c = scipy.vstack((a, b))
    audiolab.wavwrite(c, 'hidden.wav', fs, enc)
    print("New file saved as 'hidden.wav'")

else:
  print("Your input is not correct!")
  sys.exit()

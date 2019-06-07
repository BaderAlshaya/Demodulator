import sys
import wave as wav
import struct as st
import math as mt
import scipy
import numpy as np
import audiolab


def get_first_frequency(seedno):
    np.random.seed(seedno)
    if seedno > 7500:
        return np.random.randint(25001, 30000)
    return np.random.randint(20000, 25000)

def get_next_frequency(seedno):
    np.random.seed(seedno)
    if seedno > 25000:
        return np.random.randint(25001, 30000)
    return np.random.randint(20000, 25000)

print("Please choose one of the following options:")
print("1. Encode text into audio file.")
print("2. Decode text from audio file.")
print("3. Hide endoded message in another audio file.")
choice = int(input("Your choice: "))
print("-----------------")


###### Encode text message ######
if choice == 1:
  message_str = str(input("Enter text message to encode: "))
  # These will be recalculated after each window for cryptographic security
  seed_mark_int = int(input("Enter the key for the mark frequencies (value between 7501 and 15000): "))
  seed_space_int = int(input("Enter the key for the space frequencies (value between 1500 and 7500): "))
  #Translates message from ascii to a binary list
  def message_to_bin(msg):
      out = []
      for i in msg:
          byte = []
          inInt= ord(i)
          top = 128
          byte.append(0)
          while top > 1:
              if (inInt/top) >= 1:
                  byte.append(1)
                  inInt -= top
              else:
                  byte.append(0)
              top = top/2
          byte.append(int(inInt))
          byte.append(1)
          for i in byte[-1::-1]:
              out.append(i)
      return out
  #turns current byte into a sine wave and writes it to the file
  def write_sine(bit, myFile, mark_freq, space_freq):
      sine_wave = []
      if bit == 1:
          sine_wave = [np.sin(2 * np.pi * float(mark_freq) * i / 48000) for i in range(160)]
      else:
          sine_wave = [np.sin(2 * np.pi * float(space_freq) * i / 48000) for i in range(160)]
      for i in sine_wave:
          myFile.writeframes(st.pack("h", int(i*pow(2, 14))))

  #creates a .wav file and the calls write_sine() to fill it
  def build_a_wav(filename):
      wavefile = wav.open(filename, 'wb')
      wavefile.setnchannels(1)
      wavefile.setsampwidth(2)
      wavefile.setframerate(48000)
      wavefile.setnframes(sizeof)
      wavefile.setcomptype('NONE', 'nocompression')
      mark_freq = get_first_frequency(seed_mark_int)
      space_freq = get_first_frequency(seed_space_int)
      for i in bits:
          write_sine(i, wavefile, mark_freq, space_freq)
          mark_freq = get_next_frequency(mark_freq)
          space_freq = get_next_frequency(space_freq)
      wavefile.close()

  filename = str(input("Please input a name for your file (include .wav)"))
  bits = message_to_bin(message_str)
  sizeof = len(bits)*160
  build_a_wav(filename)
  print("Built your encoded wav file: " +filename+".wav")
  

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
  mark_freq = get_first_frequency(seed_mark_int) # Mark frequency. (updated for crypto)
  space_freq = get_first_frequency(seed_space_int) # Space frequency. (updated for crypto)

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
  def get_FSK(mark_freq, space_freq):
      bits = []
      # Iterate through the frames by sample size (160 frames/sample)
      for i in range(0, len(wav_floats), sample_size):
          # Get the next sample (160 frames)
          curr_sample = wav_floats[i: i + sample_size]

          # Get the mark/space size
          mark_size = filter(curr_sample, mark_freq)
          space_size = filter(curr_sample, space_freq)
		
          #Update mark and space Frequency
          mark_freq = get_next_frequency(mark_freq)
          space_freq = get_next_frequency(space_freq)
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


  print(get_message(get_FSK(mark_freq, space_freq)))  # Print the hidden message


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

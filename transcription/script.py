#!/usr/bin/env python3
import os
from io import BytesIO
from pathlib import Path

import librosa
import numpy as np
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv
from openai import OpenAI
from pydub import AudioSegment

# Get OpenAI key
load_dotenv()
if 'OPENAI_API_KEY' not in os.environ:
    raise RuntimeError("OPENAI_API_KEY is not set. Please add it to a .env file or export it to your shell.")

# Setup var path
var_dir = Path("var/")
var_dir.mkdir(exist_ok=True)

def record_audio(duration=10, samplerate=44100):
    """Record audio from the microphone."""
    print("Recording...")
    # Adjust the `channels` parameter to 1 since the MacBook Pro Microphone supports only 1 input channel
    myrecording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float64')
    sd.wait()  # Wait until recording is finished
    print("Done recording.")
    return myrecording

audio_data = record_audio(duration=5)  # Record 5 seconds of audio


# Convert the recorded audio data from a 2D NumPy array to 1D
mono_audio = audio_data.flatten()

# Compute the short-time Fourier transform (STFT)
stft = librosa.stft(mono_audio)
db = librosa.amplitude_to_db(np.abs(stft), ref=np.max)

# Compute avg volume
average_volume = np.mean(db)
print("Average volume:", average_volume)

# Save the recorded audio to a WAV file
record_audio_path = var_dir/'recorded_audio.wav'
sf.write(record_audio_path, mono_audio, 44100)

# Load the audio file with pydub
audio_segment = AudioSegment.from_file(record_audio_path, format="wav")

# Example: Cut the first 3000 milliseconds (3 seconds) of audio
# cut_audio = audio_segment[:3000]

# If you need to save the cut audio
# cut_audio.export("cut_audio.wav", format="wav")

client = OpenAI()

audio_file= open(record_audio_path, "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file,
)
print(transcription.text)
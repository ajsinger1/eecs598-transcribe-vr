#!/usr/bin/env python3
import sounddevice as sd
import numpy as np
import librosa
from pydub import AudioSegment
from io import BytesIO
import soundfile as sf
from openai import OpenAI
from pathlib import Path


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

# Add API key
key = ""

client = OpenAI(api_key=key)

audio_file= open(record_audio_path, "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file,
)
print(transcription.text)
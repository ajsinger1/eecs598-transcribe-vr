#!/usr/bin/env python3
import argparse
import io
import os
from datetime import datetime, timedelta
from queue import Queue
from sys import platform
from time import sleep
import socketserver
import sys

import speech_recognition as sr
from dotenv import load_dotenv
from openai import OpenAI

parser = argparse.ArgumentParser()
# parser.add_argument("--model", default="medium", help="Model to use",
                    # choices=["tiny", "base", "small", "medium", "large"])
# parser.add_argument("--non_english", action='store_true',
                    # help="Don't use the english model.")
parser.add_argument("--energy_threshold", default=1000,
                    help="Energy level for mic to detect.", type=int)
parser.add_argument("--record_timeout", default=2,
                    help="How real time the recording is in seconds.", type=float)
parser.add_argument("--phrase_timeout", default=3,
                    help="How much empty space between recordings before we "
                            "consider it a new line in the transcription.", type=float)
parser.add_argument("--pause_timeout", default=0.2,
                    help="How much silence before a chunk of audio is transcribed "
                            "consider it a new line in the transcription.", type=float)
if 'linux' in platform:
    parser.add_argument("--default_microphone", default='pulse',
                        help="Default microphone name for SpeechRecognition. "
                                "Run this with 'list' to view available Microphones.", type=str)
args = parser.parse_args()

# Get OpenAI key
load_dotenv()
if 'OPENAI_API_KEY' not in os.environ:
    raise RuntimeError("OPENAI_API_KEY is not set. Please add it to a .env file or export it to your shell.")

client = OpenAI()

# The last time a recording was retrieved from the queue.
phrase_time = None
# Thread safe Queue for passing data from the threaded recording callback.
data_queue = Queue()
# We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
recorder = sr.Recognizer()
recorder.energy_threshold = args.energy_threshold
recorder.pause_threshold = args.pause_timeout
# Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
recorder.dynamic_energy_threshold = False

# Important for linux users.
# Prevents permanent application hang and crash by using the wrong Microphone
if 'linux' in platform:
    mic_name = args.default_microphone
    if not mic_name or mic_name == 'list':
        print("Available microphone devices are: ")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"Microphone with name \"{name}\" found")
        sys.exit(1)
    else:
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            if mic_name in name:
                source = sr.Microphone(sample_rate=16000, device_index=index)
                break
else:
    source = sr.Microphone(sample_rate=16000)

# Load / Download model
# model = args.model
# if args.model != "large" and not args.non_english:
#     model = model + ".en"
# audio_model = whisper.load_model(model)

record_timeout = args.record_timeout
phrase_timeout = args.phrase_timeout

transcription = [[]]

with source:
    recorder.adjust_for_ambient_noise(source)

def record_callback(_, audio:sr.AudioData) -> None:
    """
    Threaded callback function to receive audio data when recordings finish.
    audio: An AudioData containing the recorded bytes.
    """
    # Grab the raw bytes and push it into the thread safe queue.
    
    data = audio.get_wav_data()
    data_queue.put(data)

    

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def setup(self) -> None:
        super().setup()
        print("Connection made. Starting recording daemon.")
        self.stop_recording = recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    def handle(self):
        global phrase_time
        # self.request is the TCP socket connected to the client)
        self.request.sendall(b"<BEGINNING TRANSCRIPTION TRANSMISSION>\n")

        to_send = []
        
        while True:
            try:
                now = datetime.now()
                # Pull raw recorded audio from the queue.
                if not data_queue.empty():
                    phrase_complete = False
                    # If enough time has passed between recordings, consider the phrase complete.
                    # Clear the current working audio buffer to start over with the new data.
                    if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                        phrase_complete = True
                    # This is the last time we received new audio data from the queue.
                    phrase_time = now
                    
                    # Combine audio data from queue
                    audio_bytes = b''.join(data_queue.queue)
                    data_queue.queue.clear()
                    with io.BytesIO(audio_bytes) as audio:
                        audio.name = "audio.wav"
                        transcription_chunk = client.audio.transcriptions.create(model="whisper-1", file=audio)

                        # If we detected a pause between recordings, add a new item to our transcription.
                        # Otherwise edit the existing one.
                        if phrase_complete:
                            transcription.append([transcription_chunk.text])
                        else:
                            transcription[-1].append(transcription_chunk.text)

                    # Clear the console to reprint the updated transcription.
                    os.system('cls' if os.name=='nt' else 'clear')
                    self.request.sendall(b'<FLUSH>')
                    for words in transcription:
                        phrase = ' '.join(words)
                        self.request.sendall(bytes(phrase + ' ', 'utf-8'))
                        print(phrase)
                    # Flush stdout.
                    print('', end='', flush=True)
                else:
                    # Infinite loops are bad for processors, must sleep.
                    sleep(0.25)
            except KeyboardInterrupt as exc:
                self.stop_recording()
                raise KeyboardInterrupt() from exc

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        print("Listening for TCP connection on localhost:9999...")
        server.serve_forever()

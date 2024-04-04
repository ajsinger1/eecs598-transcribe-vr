import io
import os
import sys
import threading
from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from typing import Optional
import logging

import speech_recognition as sr
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TranscriberArgs(BaseModel):
    energy_threshold: int = Field(
        default=1000,
        description="Energy threshold for microphone detection (lower values will make microphone more sensitive)",
    )
    record_timeout: float = Field(
        default=0.5, description="Max audio chunk duration in seconds"
    )
    phrase_timeout: float = Field(
        default=3,
        description="How much empty space between recordings before we consider it a new line in the transcription.",
    )
    pause_timeout: float = Field(
        default=0.5,
        description="How much silence before a chunk of audio is transcribed consider it a new line in the transcription.",
    )
    microphone: Optional[str] = Field(
        default="pulse" if "linux" in sys.platform else None,
        description="Microphone name for SpeechRecognition. Run this with 'list' to view available Microphones.",
    )


class Transcriber:
    """Class for creating transcriptions. Places transcriptions in a queue you can get from get_transcription_queue"""
    def __init__(self, args: TranscriberArgs):
        load_dotenv()
        if "OPENAI_API_KEY" not in os.environ:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Please add it to a .env file or export it to your shell."
            )
        self.openai_client = OpenAI()
        self.audio_queue = Queue()
        self.transcription_queue = Queue()
        self.phrase_timeout = args.phrase_timeout

        recorder = sr.Recognizer()
        recorder.energy_threshold = args.energy_threshold
        recorder.pause_threshold = args.pause_timeout
        recorder.dynamic_energy_threshold = False

        self.mic = self._get_microphone(args.microphone)
        print("Be quiet! Adjusting configuration based on ambient noise...")
        with self.mic:
            recorder.adjust_for_ambient_noise(self.mic, duration=2)
        sleep(1)
        print("Done.")
        self.stop_recording = recorder.listen_in_background(
            self.mic, self._record_callback, phrase_time_limit=args.record_timeout
        )
        self.stop_transcribing = self._transcribe()
        print("Transcriber is listening...")

    def __del__(self):
        self.stop_recording()
        self.stop_transcribing()

    def get_transcription_queue(self):
        """Getter for the queue container which holds transcriptions"""
        return self.transcription_queue

    def _transcribe(self):
        running = [True]

        def threaded_transcribe() -> None:
            last_transcribe_time = None
            phrase_audio_data = b""
            while running[0]:
                now = datetime.now()
                if not self.audio_queue.empty():
                    phrase_complete = False
                    # If enough time has passed between recordings, consider the phrase complete.
                    # Clear the current working audio buffer to start over with the new data.
                    if last_transcribe_time and now - last_transcribe_time > timedelta(
                        seconds=self.phrase_timeout
                    ):
                        phrase_complete = True
                        phrase_audio_data = b""
                    # This is the last time we received new audio data from the queue.
                    last_transcribe_time = now

                    # Combine audio data from queue
                    phrase_audio_data += b"".join(self.audio_queue.queue)
                    wav_bytes = sr.AudioData(phrase_audio_data, self.mic.SAMPLE_RATE, self.mic.SAMPLE_WIDTH).get_wav_data()
                    
                    self.audio_queue.queue.clear()
                    with io.BytesIO(wav_bytes) as audio:
                        audio.name = "audio.wav"
                        start = datetime.now()
                        transcription_chunk = (
                            self.openai_client.audio.transcriptions.create(
                                model="whisper-1", file=audio
                            )
                        )
                        end = datetime.now()
                        logger.debug("OpenAI call latency: %s", str(end - start))
                        phrase = transcription_chunk.text
                        payload = b"<P><" if phrase_complete else b"<"
                        payload += str(len(phrase)).encode() + b">" + phrase.encode()
                        self.transcription_queue.put(payload)
                        print(payload.decode())
                else:
                    # Infinite loops are bad for processors, must sleep.
                    sleep(0.25)

        def stopper(wait_for_stop=True) -> None:
            running[0] = False
            if wait_for_stop:
                transcribe_thread.join()  # block until the background thread is done, which can take around 1 second

        transcribe_thread = threading.Thread(target=threaded_transcribe)
        transcribe_thread.daemon = True
        transcribe_thread.start()
        return stopper

    def _record_callback(self, _, audio: sr.AudioData) -> None:
        """
        Callback function to receive audio data when recordings finish.
        https://github.com/Uberi/speech_recognition/blob/master/reference/library-reference.rst#recognizer_instancelisten_in_backgroundsource-audiosource-callback-callablerecognizer-audiodata-any---callablebool-none
        """
        # Grab the raw bytes and push it into the thread safe queue.
        logger.debug("Record callback entered at %s", str(datetime.now()))
        data = audio.get_raw_data()
        self.audio_queue.put(data)

    def _get_microphone(self, mic_name: str) -> sr.Microphone:
        """Sets up and returns microphone object to be used by the recorder"""
        print(f"MICROPHONE NAME: {mic_name}")
        if mic_name == "list":
            print("Available microphone devices are: ")
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f'Microphone with name "{name}" found')
            sys.exit(0)
        if mic_name is not None:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if mic_name in name:
                    return sr.Microphone(sample_rate=16000, device_index=index)
        return sr.Microphone(sample_rate=16000)

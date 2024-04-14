#!/usr/bin/env python3
import argparse
import logging
import socket
import sys
from time import sleep

import speech_recognition as sr
from transcriber import Transcriber, TranscriberArgs

logger = logging.getLogger(__name__)

def initialize_logger(args):
    """Initialize the logging module"""
    try:
        logging.basicConfig(level=args.log_level)
    except ValueError:
        logging.error("Invalid log level: %s", args.log_level)
        sys.exit(1)

def parse_args():
    """Parse Arguments"""
    parser = argparse.ArgumentParser()
    # Logging args
    parser.add_argument("--log-level", default="WARNING", help="Set log level. (default is WARNING)", type=str)
    # Networking Related Args
    parser.add_argument(
        "-a",
        "--address",
        default="127.0.0.1",
        help="Host address to connect to. (default is 127.0.0.1)",
        type=str,
    )
    parser.add_argument(
        "-p", "--port", default=9000, help="Port to connect to. (default is 9000)", type=int
    )

    # Transcription Related Args
    for name, field in TranscriberArgs.model_fields.items():
        parser.add_argument(
            f"--{name}",
            default=field.default,
            help=field.description + f" (default is {field.default})",
            type=field.annotation,
        )

    return parser.parse_args()

def get_microphone(mic_name: str) -> sr.Microphone:
    """Sets up and returns microphone object to be used by the recorder"""
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


def main(args):
    """Script entry point"""
    transcriber = Transcriber(TranscriberArgs(**vars(args)))
    transcription_queue = transcriber.get_transcription_queue()
    while True:
        try:
            print("Attempting to connect...")
            sock = socket.create_connection((args.address, args.port))
        except OSError:
            print ("Could not connect. Will retry in 5 seconds...")
            sleep(5)
            continue
        print("Connected.")
        while True:
            data = b""
            while not transcription_queue.empty():
                data += transcription_queue.get()
            try:
                sock.sendall(data)
            except OSError as e:
                print(e)
                break


if __name__ == "__main__":
    args_map = parse_args()
    initialize_logger(args_map)
    main(args_map)

#!/usr/bin/env python3
import cv2
import logging
import sys
import argparse
from face_collection import FaceCollection
from transcription_server import TranscriptionServer

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

    # Networking args
    parser.add_argument(
        "-a",
        "--address",
        default="127.0.0.1",
        help="Host address to listen on. (default is 127.0.0.1)",
        type=str,
    )
    parser.add_argument(
        "-p", "--port", default=9000, help="Port to listen on. (default is 9000)", type=int
    )
    
    # Recognition args
    parser.add_argument(
        "-m", "--mar-deque-length", default=10, help="length of MAR deque. (default is 10)", type=int
    )

    parser.add_argument(
        "-t", "--talk-threshold", default=0.05, help="talk threshold (minimum average MAR to be considered \"talking\"). (default is 0.05)", type=float
    )

    return parser.parse_args()

def main(args):
    video_capture = cv2.VideoCapture(0)
    face_collection = FaceCollection(args.mar_deque_length, args.talk_threshold)
    transcription_server = TranscriptionServer(args.address, args.port)

    while True:
        result, video_frame = video_capture.read()
        if not result:
            sys.exit(1)
        face_collection.update(video_frame)
        speaker = face_collection.get_speaker()
        if speaker:
            is_new_phrase, phrase = transcription_server.get_phrase()
            cv2.putText(video_frame, phrase, (speaker.coordinates.x, speaker.coordinates.y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
       
        cv2.imshow("My Face Detection Project", video_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            sys.exit(0)


if __name__ == "__main__":
    args_map = parse_args()
    initialize_logger(args_map)
    main(args_map)
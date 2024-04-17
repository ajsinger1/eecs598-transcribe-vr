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
        "-m", "--mar-deque-length", default=25, help="length of MAR deque. (default is 10)", type=int
    )

    parser.add_argument(
        "-t", "--talk-threshold", default=0.05, help="talk threshold (minimum average MAR to be considered \"talking\"). (default is 0.05)", type=float
    )

    return parser.parse_args()

def main(args):
    video_capture = cv2.VideoCapture(0)
    face_collection = FaceCollection(args.mar_deque_length, args.talk_threshold)
    transcription_server = TranscriptionServer(args.address, args.port)

    old_phrase = ''
    prev_speaker = None
    while True:
        result, video_frame = video_capture.read()
        if not result:
            sys.exit(1)
        face_collection.update(video_frame)
        speaker = face_collection.get_speaker()
        if prev_speaker is None:
            prev_speaker = speaker
        if speaker and speaker.is_talking():
            is_new_phrase, phrase = transcription_server.get_phrase()
            new_phrase = phrase
            if speaker != prev_speaker and len(phrase) >= len(old_phrase):
                print(f"{speaker.get_id()}: {phrase}")
                diff = len(phrase) - len(old_phrase)
                new_phrase = phrase[-diff:] if diff != 0 else ""
                print(f"{speaker.get_id()}: {new_phrase}")
            prev_speaker = speaker
            speaker.set_words(new_phrase)
            old_phrase = phrase
            

        
        for face in face_collection.faces:
            recently_spoken = face.get_words()
            if len(recently_spoken) < 40:
                cv2.putText(video_frame, f"{face.get_id()}: {recently_spoken}", (face.coordinates.x, face.coordinates.y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                cv2.putText(video_frame, f"{face.get_id()}: {recently_spoken[-40:]}", (face.coordinates.x, face.coordinates.y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

       
        cv2.imshow("My Face Detection Project", video_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            sys.exit(0)


if __name__ == "__main__":
    args_map = parse_args()
    initialize_logger(args_map)
    main(args_map)

# fix MAR and whos talking
# words should be 'glued' to one persons face so that old text doesnt go to new face
# user testing with a script (inside)
    # qualifying effectiveness of tool
    # how accurate is speech to text
    # how correct are we with assignment
# user test #2 (outside people)
    # maybe get zoom input
    # can we have an effective conversation
    # paper due next friday
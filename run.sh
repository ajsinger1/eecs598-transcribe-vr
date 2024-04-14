#!/usr/bin/env bash
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
cd ./recognition
if [ ! -d "env" ]; then
    echo "recognition env not foumd. Creating..."
    python3 -m venv env;
    source env/bin/activate;
    pip install -r ./requirements.txt;
fi

source env/bin/activate;

if [ "$1" = "debug" ]; then
    ./recognition.py --log-level DEBUG &
else
    ./recognition.py &
fi

deactivate

cd ../transcription
if [ ! -d "env" ]; then
    echo "transcription env not foumd. Creating..."
    python3 -m venv env;
    source env/bin/activate;
    pip install -r ./requirements.txt;
fi

source env/bin/activate;

if [ "$1" = "debug" ]; then
    ./rtt.py
else
    ./rtt.py
fi
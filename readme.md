# Real Time Transcription (VR)
### Python Development
#### Setup
Add OpenAI API key to dotenv file
```zsh
cd transcription
echo "OPENAI_API_KEY={API_KEY_HERE}" > .env 
```

Create virtual env and install dependencies
```zsh
cd transcription
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

#### Usage
```zsh
cd transcription
source env/bin/activate # activate the python environment
./script.py
```

regonition uses lip movement detector
recog only uses MAR
Neither really work that well
```zsh
cd recognition
source env/bin/activate # activate the python environment
python3 recognition.py
or
python3 recog.py
```

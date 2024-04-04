# Real Time Transcription (VR)
### RTT Development
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
./rtt.py
```

#### Tuning `rtt.py`
`./rtt.py --help` to look at the arguments

If you find that you are speaking, but it is not consistently transcribing, the energy_threshold is most likely the issue. The optimal setting for this parameter is dependent on ambient noise. If you are in a quiet environment, try running `./rtt.py --energy_threshold 50`

#### Testing `rtt.py` locally
Open two shells and run `rtt.py` and `dummy_server.py`

### Recognition Development
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

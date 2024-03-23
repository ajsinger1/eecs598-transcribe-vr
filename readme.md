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

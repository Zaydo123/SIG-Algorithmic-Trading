# Sentiment Analysis Project

## Getting Started

### 1) Setup virtual environment
```bash
python3 -m venv ./venv
```
### 2) Activate the virtual environment
```bash
source ./venv/bin/activate
```
### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Run the application
```bash
python getSentiment.py
```

## Common Issues

### 1) SSL Errors related to feedparser library on MacOS - Solution
execute the following command in the terminal, replacing the major version number with the version of Python you are using.
```bash
open /Applications/Python\ 3.12/Install\ Certificates.command
```
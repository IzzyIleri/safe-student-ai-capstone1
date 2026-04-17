# SafeStudent AI – Phishing Detection Backend

## Overview

SafeStudent AI is a Flask-based backend system that analyzes email content and assigns a phishing risk score. The system evaluates suspicious indicators such as urgency language, credential requests, and embedded links.

## Features

* Risk scoring system (0–100)
* Detection of phishing indicators
* REST API endpoint for analysis
* Real-time integration with Chrome extension

## Tech Stack

* Python
* Flask
* Flask-CORS

## How It Works

1. Email content is extracted from Gmail (via Chrome extension)
2. The content is sent to the Flask API
3. The system analyzes keywords and patterns
4. A risk score is returned with flags

## API Endpoint

POST /api/analyze

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Runs on:
http://127.0.0.1:5001

## Future Improvements

* Machine learning-based detection
* Chrome extension auto-scan
* UI dashboard

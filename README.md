# Project Membrain

![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/dominictarro/project-membrain)
![GitHub](https://img.shields.io/github/license/dominictarro/project-membrain)

An ETL pipeline for building a dataset of memes with prepared image and text analysis.

## Prerequisites

The setup script requires GNU make which is available on Linux and Macintosh systems.

1. Python 3.10
2. Docker
3. Reddit API secret & key

## Setup and Installation

Clone the repository.

>`git clone https://github.com/dominictarro/project-membrain.git`

Navigate to the directory it was cloned to.

Create a .env file like

```bash
# Required for querying Reddit memes
# Create at https://www.reddit.com/prefs/apps
REDDIT_SECRET=...
REDDIT_ID=...

# Optional, only if you want to modify logging config
LOGGING_CONFIGURATION=logging.yml

# Required for load phase
# Database name
POSTGRES_DB=...
POSTGRES_PASSWORD=...
POSTGRES_USER=...
```

Once your environment variables are set run

> `make build`

This should

1. Create a Python 3.10 virtual environment.
2. Install required packages.
3. Download required NLTK data.
4. Create the local Docker database service.
    - It may take a few minutes to pull the required images.

## Start pipeline

Open a terminal and navigate to the project

```bash
source ./venv/bin/activate
docker-compose up -d db
python3.10 main.py
```

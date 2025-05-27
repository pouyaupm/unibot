# Unibot

This repository contains simple tools for scraping pages from the University of Helsinki website and asking questions about the collected data using the OpenAI API.

## Setup

1. Create a Python virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install requests beautifulsoup4 openai
```

2. Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY=sk-...
```

You may also change `UNIBOT_DB` to specify the database path.

## Scraping

Run the scraper to download pages from the University of Helsinki (default limit 100 pages):

```bash
python scrape_helsinki.py
```

The pages will be stored in a SQLite full‑text search database `helsinki.db`.

## Asking Questions

After scraping, you can query the information with:

```bash
python qa_bot.py "Your question here"
```

The bot will search the database for relevant content and send a prompt to ChatGPT to generate an answer.

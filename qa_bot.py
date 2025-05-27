#!/usr/bin/env python3
import os
import sys
import sqlite3
import re

import openai
from dotenv import load_dotenv

# ─── 1) Load .env ───────────────────────────────────────────────────────────────
load_dotenv()
key = os.getenv("OPENAI_API_KEY")
print("Key prefix:", key[:3])   # should print "sk-"

# ─── 2) Config from ENV ───────────────────────────────────────────────────────
DB_PATH = os.getenv('UNIBOT_DB', 'helsinki.db')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    sys.exit("Error: Missing OPENAI_API_KEY in environment. Add it to your .env file.")

openai.api_key = OPENAI_API_KEY

# ─── 3) FTS5 helper ────────────────────────────────────────────────────────────
def search_context(query: str, limit: int = 5) -> str:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # strip punctuation, phrase-search
    safe = re.sub(r'[^\w\s]', '', query).strip()
    sql = '''
      SELECT url, content
      FROM pages
      WHERE pages MATCH ?
      LIMIT ?
    '''
    cur.execute(sql, (f'"{safe}"', limit))
    rows = cur.fetchall()
    conn.close()

    return "\n\n".join(f"URL: {url}\n{content}" for url, content in rows)

# ─── 4) Ask OpenAI ─────────────────────────────────────────────────────────────
def ask(question: str) -> str:
    context = search_context(question)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant with access to documentation about "
                "the University of Helsinki."
            )
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        }
    ]

    # <-- NEW v1+ API call:
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()

# ─── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "What faculties are at the University of Helsinki?"
    print(ask(question))

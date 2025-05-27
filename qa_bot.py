import os
import sqlite3
import openai

DB_PATH = os.getenv('UNIBOT_DB', 'helsinki.db')
openai.api_key = os.getenv('OPENAI_API_KEY')


def search_context(query: str, limit: int = 5):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT url, content FROM pages WHERE pages MATCH ? LIMIT ?', (query, limit))
    rows = cur.fetchall()
    conn.close()
    context = "\n\n".join(f"URL: {url}\n{content}" for url, content in rows)
    return context


def ask(question: str) -> str:
    context = search_context(question)
    prompt = (
        "You are a helpful assistant with access to documentation about the University of Helsinki.\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\nAnswer:"
    )
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=200
    )
    return response.choices[0].text.strip()


if __name__ == '__main__':
    import sys
    question = " ".join(sys.argv[1:]) or "What faculties are at the University of Helsinki?"
    print(ask(question))

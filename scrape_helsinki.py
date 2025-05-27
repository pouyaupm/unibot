import os
import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

DB_PATH = os.getenv('UNIBOT_DB', 'helsinki.db')
BASE_URL = 'https://www.helsinki.fi/en'

# ensure database and FTS table
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute('CREATE VIRTUAL TABLE IF NOT EXISTS pages USING fts5(url, content)')
conn.commit()


def save_page(url: str, content: str):
    cur.execute('INSERT OR REPLACE INTO pages(url, content) VALUES (?, ?)', (url, content))
    conn.commit()


def scrape_site(start_url=BASE_URL, max_pages=100):
    visited = set()
    queue = deque([start_url])

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        save_page(url, soup.get_text(separator=' ', strip=True))
        print(f"Saved {url}")

        for link in soup.find_all('a', href=True):
            href = urljoin(url, link['href'])
            parsed = urlparse(href)
            if parsed.scheme.startswith('http') and parsed.netloc.endswith('helsinki.fi'):
                if '#' in parsed.path:
                    href = href.split('#')[0]
                if href not in visited:
                    queue.append(href)

    print(f"Scraped {len(visited)} pages")


if __name__ == '__main__':
    scrape_site()
    conn.close()

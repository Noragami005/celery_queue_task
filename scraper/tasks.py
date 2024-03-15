import requests
from celery import shared_task
from bs4 import BeautifulSoup
import sqlite3


@shared_task
def scrape_proxies():
    url = 'https://geonode.com/free-proxy-list'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    proxies = []
    for row in soup.find_all('tr')[1:]:
        cells = row.find_all('td')
        if len(cells) >= 5:
            ip, port, protocol, country, uptime = cells[:5]
            proxies.append({
                'ip': ip.text.strip(),
                'port': port.text.strip(),
                'protocol': protocol.text.strip(),
                'country': country.text.strip(),
                'uptime': uptime.text.strip(),
            })

    with sqlite3.connect('proxies.db') as conn:
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS proxies (
            ip TEXT PRIMARY KEY,
            port TEXT,
            protocol TEXT,
            country TEXT,
            uptime TEXT
        )''')

        for proxy in proxies:
            try:
                cursor.execute('''INSERT OR IGNORE INTO proxies (ip, port, protocol, country, uptime)
                                VALUES (?, ?, ?, ?, ?)''', (proxy['ip'], proxy['port'],
                                                            proxy['protocol'], proxy['country'], proxy['uptime']))
            except sqlite3.IntegrityError:
                pass  # Ignore duplicate IP entries

        conn.commit()

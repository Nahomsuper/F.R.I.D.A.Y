import re
import requests
import xml.etree.ElementTree as ET
from tts import speak

FEEDS = {
    'top': (
        'The Times of India',
        'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
        'https://timesofindia.indiatimes.com/',
    ),
    'sports': (
        'Sports',
        'https://timesofindia.indiatimes.com/rssfeeds/4719148.cms',
        'https://timesofindia.indiatimes.com/sports/',
    ),
    'tech': (
        'Technology',
        'https://news.google.com/rss/search?q=when:24h+site:timesofindia.indiatimes.com/technology&hl=en-IN&gl=IN&ceid=IN:en',
        'https://timesofindia.indiatimes.com/technology/',
    ),
}


def _titles(feed_url):
    response = requests.get(feed_url, timeout=15)
    response.raise_for_status()
    xml_text = re.sub(
        r'<\?xml[^>]*\?>', '', response.content.decode('utf-8', errors='replace'), count=1
    )
    root = ET.fromstring(xml_text)
    titles = []
    for item in root.findall('.//item')[:8]:
        title = (item.findtext('title') or '').split(' - Times of India')[0].strip()
        if title:
            titles.append(title)
    return titles


def speak_news(kind='top'):
    source, feed_url, _ = FEEDS.get(kind, FEEDS['top'])
    try:
        titles = _titles(feed_url)
    except Exception:
        speak('News is unavailable right now.')
        return
    if not titles:
        speak('No headlines are available right now.')
        return
    speak(f'Source: {source}')
    speak('Todays headlines are')
    for index, title in enumerate(titles):
        speak(title)
        if index < len(titles) - 1:
            speak('Next headline')
    speak('These were the top headlines. Have a nice day, sir.')


def getNewsUrl(kind='top'):
    return FEEDS.get(kind, FEEDS['top'])[2]


if __name__ == '__main__':
    speak_news()

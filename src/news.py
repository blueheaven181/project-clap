import html
import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus
from googlenewsdecoder import gnewsdecoder

import requests
import trafilatura


NEWS_QUERIES = {
    "general": "United Arab Emirates latest news when:1d",
    "forex": "forex currency market news when:1d",
    "cybersecurity": "cybersecurity news when:1d",
    "ai": "artificial intelligence news when:1d",
    "technology": "technology news when:1d",
}

NEWS_LABELS = {
    "general": "general",
    "forex": "forex",
    "cybersecurity": "cybersecurity",
    "ai": "artificial intelligence",
    "technology": "technology",
}

LATEST_NEWS_ITEMS = []

OLLAMA_URL = "http://localhost:11434/api/chat"
LOCAL_AI_MODEL = "llama3.2:1b"
MAX_ARTICLE_CHARACTERS = 6000


def clean_headline(title, source):
    """
    Clean text received from the RSS feed.
    """

    cleaned_title = html.unescape(title).strip()
    cleaned_source = html.unescape(source).strip().rstrip(".")

    source_suffix = f" - {cleaned_source}"

    if cleaned_source and cleaned_title.endswith(source_suffix):
        cleaned_title = cleaned_title[
            :-len(source_suffix)
        ].strip()

    return cleaned_title, cleaned_source


def get_latest_news(category="general", headline_limit=3):
    """
    Retrieve recent headlines for a supported news category.
    """
    global LATEST_NEWS_ITEMS
    LATEST_NEWS_ITEMS = []


    normalized_category = category.strip().lower()

    if normalized_category not in NEWS_QUERIES:
        normalized_category = "general"

    query = NEWS_QUERIES[normalized_category]
    encoded_query = quote_plus(query)

    url = (
        "https://news.google.com/rss/search"
        f"?q={encoded_query}"
        "&hl=en-AE"
        "&gl=AE"
        "&ceid=AE:en"
    )

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Project-CLAP/0.7",
            },
            timeout=15,
        )
        response.raise_for_status()

        rss_root = ET.fromstring(response.content)
        news_items = rss_root.findall(".//item")

        def publication_time(news_item):
            published_text = news_item.findtext(
                "pubDate",
                default="",
            )

            try:
                return parsedate_to_datetime(
                    published_text
                ).timestamp()
            except (TypeError, ValueError):
                return 0

        news_items.sort(
            key=publication_time,
            reverse=True,
        )

        if not news_items:
            return (
                "I could not find any recent "
                f"{NEWS_LABELS[normalized_category]} headlines."
            )

        spoken_headlines = []
        seen_headlines = set()

        for news_item in news_items:
            title = news_item.findtext("title", default="")
            source = news_item.findtext("source", default="")
            link = news_item.findtext("link", default="")

            cleaned_title, cleaned_source = clean_headline(
                title,
                source,
            )

            if not cleaned_title:
                continue

            headline_key = re.sub(
                r"[^a-z0-9]+",
                " ",
                cleaned_title.lower(),
            ).strip()

            if headline_key in seen_headlines:
                continue

            seen_headlines.add(headline_key)

            LATEST_NEWS_ITEMS.append(
                {
                    "title": cleaned_title,
                    "source": cleaned_source,
                    "link": link.strip(),
                    "category": normalized_category,
                }
            )

            headline_number = len(LATEST_NEWS_ITEMS)

            number_words = {
                1: "First",
                2: "Second",
                3: "Third",
            }

            spoken_number = number_words.get(
                headline_number,
                f"Headline {headline_number}",
            )

            if cleaned_source:
                spoken_headlines.append(
                    f"{spoken_number}: {cleaned_title}. "
                    f"Source: {cleaned_source}."
                )
            else:
                spoken_headlines.append(
                    f"{spoken_number}: {cleaned_title}."
                )

            if len(spoken_headlines) >= headline_limit:
                break

        if not spoken_headlines:
            return (
                "I found the news feed, but it did not "
                "contain readable headlines."
            )

        category_label = NEWS_LABELS[normalized_category]

        return (
            f"Here are the latest {category_label} headlines. "
            + " ".join(spoken_headlines)
        )

    except requests.RequestException as error:
        print("News connection error:", error)

        return (
            "I could not retrieve the latest news. "
            "Please check your internet connection."
        )

    except ET.ParseError as error:
        print("News feed error:", error)

        return (
            "I received the news feed, but I could not read it."
        )


def get_news_item(headline_number):
    """
    Return one of the headlines remembered by CLAP.
    """

    item_index = headline_number - 1

    if item_index < 0 or item_index >= len(LATEST_NEWS_ITEMS):
        return None

    return LATEST_NEWS_ITEMS[item_index]


def resolve_google_news_link(article_link):
    """
    Convert a Google News forwarding link into the publisher's real URL.
    """

    if "news.google.com" not in article_link:
        return article_link

    try:
        decoded_result = gnewsdecoder(
            article_link,
            interval=1,
        )

        if decoded_result.get("status"):
            resolved_link = decoded_result["decoded_url"]
            print("Resolved publisher link:", resolved_link)
            return resolved_link

        print(
            "Google News link could not be resolved:",
            decoded_result.get("message", "Unknown error"),
        )

    except Exception as error:
        print("Google News link resolution error:", error)

    return article_link



def get_news_article_text(headline_number):
    """
    Download and extract readable text from a remembered article.
    """

    selected_item = get_news_item(headline_number)

    if not selected_item:
        return ""

    article_link = selected_item["link"]
    article_link = resolve_google_news_link(article_link)

    try:
        downloaded_page = trafilatura.fetch_url(
            article_link
        )

        if not downloaded_page:
            print("The article page could not be downloaded.")
            return ""

        article_text = trafilatura.extract(
            downloaded_page,
            include_comments=False,
            include_tables=False,
        )

        if not article_text:
            print("Readable article text was not found.")
            return ""

        return article_text.strip()

    except Exception as error:
        print("Article extraction error:", error)
        return ""

def summarize_news_article(headline_number):
    """
    Extract and summarize one remembered news article using Ollama.
    """

    selected_item = get_news_item(headline_number)

    if not selected_item:
        return (
            "I do not have that headline in memory. "
            "Please request the latest news first."
        )

    article_text = get_news_article_text(headline_number)

    if not article_text:
        return (
            f"The headline is {selected_item['title']}. "
            f"The source is {selected_item['source']}. "
            "I could not access enough article text to provide "
            "a reliable summary."
        )

    limited_article_text = article_text[
        :MAX_ARTICLE_CHARACTERS
    ]

    summary_prompt = f"""
Summarize the supplied news article for spoken playback.

Rules:
- Use only facts contained in the supplied article.
- Do not add assumptions or outside information.
- Give the main point first.
- Use no more than three short sentences.
- Do not use Markdown, headings, or bullet points.
- If the article text is insufficient, say so clearly.

Headline: {selected_item["title"]}
Source: {selected_item["source"]}

Article:
{limited_article_text}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": LOCAL_AI_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": summary_prompt,
                    }
                ],
                "stream": False,
                "options": {
                    "num_predict": 120,
                    "temperature": 0.1,
                },
            },
            timeout=120,
        )

        response.raise_for_status()

        summary = (
            response.json()["message"]["content"].strip()
        )

        if not summary:
            return (
                "I extracted the article, but I could not "
                "produce a summary."
            )

        return summary

    except requests.RequestException as error:
        print("News summarization connection error:", error)

        return (
            "I extracted the article, but I could not connect "
            "to my local AI engine to summarize it."
        )

    except (KeyError, TypeError, ValueError) as error:
        print("News summarization response error:", error)

        return (
            "I extracted the article, but the summary response "
            "could not be read."
        )


if __name__ == "__main__":
    print(get_latest_news("ai"))

    print("\nCLAP summary:")
    print(summarize_news_article(1))
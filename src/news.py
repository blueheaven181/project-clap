import html
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

import requests


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


def clean_headline(title, source):
    """
    Clean text received from the RSS feed.
    """

    cleaned_title = html.unescape(title).strip()
    cleaned_source = html.unescape(source).strip()

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
                "User-Agent": "Project-CLAP/0.6",
            },
            timeout=15,
        )
        response.raise_for_status()

        rss_root = ET.fromstring(response.content)
        news_items = rss_root.findall(".//item")

        if not news_items:
            return (
                "I could not find any recent "
                f"{NEWS_LABELS[normalized_category]} headlines."
            )

        spoken_headlines = []

        for news_item in news_items[:headline_limit]:
            title = news_item.findtext("title", default="")
            source = news_item.findtext("source", default="")

            cleaned_title, cleaned_source = clean_headline(
                title,
                source,
            )

            if not cleaned_title:
                continue

            if cleaned_source:
                spoken_headlines.append(
                    f"{cleaned_title}. "
                    f"Source: {cleaned_source}."
                )
            else:
                spoken_headlines.append(
                    f"{cleaned_title}."
                )

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


if __name__ == "__main__":
    print(get_latest_news("ai"))
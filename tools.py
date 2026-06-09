from langchain.tools import tool
from tavily import TavilyClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import requests
import os

load_dotenv()

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

@tool
def web_search(query: str) -> str:
    """Search web and return results."""

    result = tavily.search(
        query=query,
        max_results=5
    )

    output = []

    for item in result["results"]:

        output.append(
            f"""
Title: {item.get('title')}

URL: {item.get('url')}

Content:
{item.get('content')}
"""
        )

    return "\n\n----------------------\n\n".join(output)


@tool
def scrape_url(url: str) -> str:
    """Scrape webpage."""

    try:

        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside"
        ]):
            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        return text[:5000]

    except Exception as e:

        return f"ERROR: {str(e)}"
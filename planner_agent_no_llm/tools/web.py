import requests
from bs4 import BeautifulSoup

def fetch_text(url: str, max_chars: int = 2000) -> str:
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # remove scripts/styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = " ".join(soup.get_text(" ").split())
        return text[:max_chars] + ("..." if len(text) > max_chars else "")
    except Exception as e:
        return f"❌ Web fetch error: {e}"

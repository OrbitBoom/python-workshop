"""Network adapters for the desktop forms. Each request has a time limit."""

import html
import json
import ssl
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def tls_context():
    context = ssl.create_default_context()
    # Some python.org macOS installations have no configured OpenSSL CA bundle.
    if (
        sys.platform == "darwin"
        and not context.get_ca_certs()
        and Path("/etc/ssl/cert.pem").is_file()
    ):
        context.load_verify_locations("/etc/ssl/cert.pem")
    return context


def get_json(url, params=None):
    if params:
        url += "?" + urlencode(params)
    request = Request(
        url,
        headers={
            "User-Agent": "PythonWorkshop/1.0 (github.com/OrbitBoom/python-workshop)"
        },
    )
    with urlopen(request, timeout=10, context=tls_context()) as response:
        return json.load(response)


def search(topic):
    if not topic.strip():
        raise ValueError("Enter a topic.")
    data = get_json(
        "https://en.wikipedia.org/w/api.php",
        {
            "action": "query",
            "generator": "search",
            "gsrsearch": topic,
            "gsrlimit": 1,
            "prop": "extracts",
            "exintro": 1,
            "explaintext": 1,
            "exsentences": 4,
            "format": "json",
        },
    )
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return "No articles found."
    page = next(iter(pages.values()))
    return (
        page["title"] + "\n\n" + (page.get("extract") or "No introduction available.")
    )


def translate(text, source, target):
    if not text.strip() or len(text.encode()) > 500:
        raise ValueError("Enter 1–500 bytes of text.")
    if source == target:
        return text
    data = get_json(
        "https://api.mymemory.translated.net/get",
        {"q": text, "langpair": f"{source}|{target}"},
    )
    if str(data.get("responseStatus")) != "200":
        raise ValueError(data.get("responseDetails") or "Translation unavailable.")
    return html.unescape(data["responseData"]["translatedText"])

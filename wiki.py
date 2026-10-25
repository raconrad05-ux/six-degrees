import requests

API_URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "SixDegreesOfWikipedia/1.0 (your-email@scu.edu)"}
TIMEOUT = 10


def resolve_title(title):
    """Return the official title of an article, following redirects, or None if it doesn't exist."""
    params = {
        "action": "query",
        "titles": title,
        "redirects": 1,
        "format": "json",
        "formatversion": 2,
    }
    response = requests.get(API_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", [])
    if not pages:
        return None
    page = pages[0]
    if page.get("missing") or page.get("invalid"):
        return None
    return page["title"]


def get_links(title):
    """Return a list of all article titles linked from the given article."""
    params = {
        "action": "query",
        "titles": title,
        "prop": "links",
        "plnamespace": 0,
        "pllimit": "max",
        "format": "json",
        "formatversion": 2,
    }
    links = []
    while True:
        response = requests.get(API_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        for page in data.get("query", {}).get("pages", []):
            for link in page.get("links", []):
                links.append(link["title"])
        if "continue" not in data:
            break
        params.update(data["continue"])
    return links

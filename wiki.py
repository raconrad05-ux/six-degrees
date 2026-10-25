from collections import deque

import requests

API_URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "SixDegreesOfWikipedia/1.0 (rconrad@scu.edu)"}
TIMEOUT = 10


def api_get(params):
    """Send one request to the Wikipedia API and return the JSON response."""
    response = requests.get(API_URL, params=params, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def resolve_title(title):
    """Return the official title of an article, following redirects, or None if it doesn't exist."""
    params = {
        "action": "query",
        "titles": title,
        "redirects": 1,
        "format": "json",
        "formatversion": 2,
    }
    pages = api_get(params).get("query", {}).get("pages", [])
    if not pages:
        return None
    page = pages[0]
    if page.get("missing") or page.get("invalid"):
        return None
    return page["title"]


def search_title(query):
    """Return the title of the closest matching article, or None if nothing matches."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": 0,
        "srlimit": 1,
        "format": "json",
        "formatversion": 2,
    }
    results = api_get(params).get("query", {}).get("search", [])
    if not results:
        return None
    return results[0]["title"]


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
        data = api_get(params)
        for page in data.get("query", {}).get("pages", []):
            for link in page.get("links", []):
                links.append(link["title"])
        if "continue" not in data:
            break
        params.update(data["continue"])
    return links


def find_path(start, end, max_articles=300):
    """Use breadth-first search to find the shortest chain of links from start to end."""
    if start == end:
        return {"path": [start], "articles_checked": 0}

    queue = deque([start])
    visited = {start}
    parent = {start: None}
    articles_checked = 0

    while queue and articles_checked < max_articles:
        current = queue.popleft()
        links = get_links(current)
        articles_checked += 1

        for link in links:
            if link in visited:
                continue
            visited.add(link)
            parent[link] = current
            if link == end:
                path = []
                node = end
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return {"path": path, "articles_checked": articles_checked}
            queue.append(link)

    return {"path": None, "articles_checked": articles_checked}

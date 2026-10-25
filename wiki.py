import time

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


def get_backlinks(title, max_links=2500):
    """Return a list of article titles that link to the given article, up to max_links."""
    params = {
        "action": "query",
        "list": "backlinks",
        "bltitle": title,
        "blnamespace": 0,
        "blredirect": 1,
        "bllimit": "max",
        "format": "json",
        "formatversion": 2,
    }
    backlinks = []
    while len(backlinks) < max_links:
        data = api_get(params)
        for page in data.get("query", {}).get("backlinks", []):
            backlinks.append(page["title"])
            # Articles that link through a redirect (e.g. "USA") are listed under it.
            for redirect_link in page.get("redirlinks", []):
                backlinks.append(redirect_link["title"])
        if "continue" not in data:
            break
        params.update(data["continue"])
    return backlinks[:max_links]


def build_path(meeting, forward_parent, backward_parent):
    """Join the forward chain (start to meeting) with the backward chain (meeting to end)."""
    path = []
    node = meeting
    while node is not None:
        path.append(node)
        node = forward_parent[node]
    path.reverse()
    node = backward_parent[meeting]
    while node is not None:
        path.append(node)
        node = backward_parent[node]
    return path


def find_path(start, end, max_articles=300, max_seconds=60):
    """Use bidirectional breadth-first search to find the shortest chain of links from start to end."""
    if start == end:
        return {"path": [start], "articles_checked": 0}

    forward = {"fetch": get_links, "parent": {start: None}, "depth": {start: 0}, "frontier": [start]}
    backward = {"fetch": get_backlinks, "parent": {end: None}, "depth": {end: 0}, "frontier": [end]}
    articles_checked = 0
    began = time.monotonic()
    best_length = None
    meeting = None
    out_of_budget = False

    while forward["frontier"] and backward["frontier"] and meeting is None and not out_of_budget:
        # Expand one full layer of whichever side has the smaller frontier.
        if len(forward["frontier"]) <= len(backward["frontier"]):
            side, other = forward, backward
        else:
            side, other = backward, forward

        next_frontier = []
        for current in side["frontier"]:
            if articles_checked >= max_articles or time.monotonic() - began >= max_seconds:
                out_of_budget = True
                break
            neighbors = side["fetch"](current)
            articles_checked += 1

            for neighbor in neighbors:
                if neighbor in side["parent"]:
                    continue
                side["parent"][neighbor] = current
                side["depth"][neighbor] = side["depth"][current] + 1
                next_frontier.append(neighbor)
                if neighbor in other["parent"]:
                    length = side["depth"][neighbor] + other["depth"][neighbor]
                    if best_length is None or length < best_length:
                        best_length = length
                        meeting = neighbor
        side["frontier"] = next_frontier

    if meeting is None:
        return {"path": None, "articles_checked": articles_checked}
    path = build_path(meeting, forward["parent"], backward["parent"])
    return {"path": path, "articles_checked": articles_checked}

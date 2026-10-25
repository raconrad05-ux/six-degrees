import time
from urllib.parse import quote

import requests
from flask import Flask, render_template, request

from wiki import find_path, resolve_title, search_title

app = Flask(__name__)

UNREACHABLE = "Couldn't reach Wikipedia right now. Please try again."


def wiki_url(title):
    return "https://en.wikipedia.org/wiki/" + quote(title.replace(" ", "_"))


def lookup(query, notes):
    """Return the article title for what the user typed, or None if there's no match."""
    title = resolve_title(query)
    if title is None:
        title = search_title(query)
        if title is not None:
            notes.append(f"Showing results for {title}")
    return title


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/path')
def path():
    start_query = request.args.get("start", "").strip()
    end_query = request.args.get("end", "").strip()

    def form_error(message):
        return render_template("index.html", error=message, start=start_query, end=end_query)

    if not start_query or not end_query:
        return form_error("Please enter both articles.")

    notes = []
    try:
        start = lookup(start_query, notes)
        if start is None:
            return form_error(f"No Wikipedia article called {start_query}.")
        end = lookup(end_query, notes)
        if end is None:
            return form_error(f"No Wikipedia article called {end_query}.")

        began = time.perf_counter()
        result = find_path(start, end)
        seconds = round(time.perf_counter() - began, 1)
    except requests.exceptions.RequestException:
        return form_error(UNREACHABLE)

    chain = None
    if result["path"]:
        chain = [(title, wiki_url(title)) for title in result["path"]]

    return render_template(
        "result.html",
        start=start,
        end=end,
        notes=notes,
        chain=chain,
        articles_checked=result["articles_checked"],
        seconds=seconds,
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500

import time
from urllib.parse import quote

from flask import Flask, render_template, request

from wiki import find_path, resolve_title

app = Flask(__name__)


def wiki_url(title):
    return "https://en.wikipedia.org/wiki/" + quote(title.replace(" ", "_"))


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/path')
def path():
    start = resolve_title(request.args.get("start", ""))
    end = resolve_title(request.args.get("end", ""))

    began = time.perf_counter()
    result = find_path(start, end)
    seconds = round(time.perf_counter() - began, 1)

    chain = None
    if result["path"]:
        chain = [(title, wiki_url(title)) for title in result["path"]]

    return render_template(
        "result.html",
        start=start,
        end=end,
        chain=chain,
        articles_checked=result["articles_checked"],
        seconds=seconds,
    )

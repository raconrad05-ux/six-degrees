# Six Degrees of Wikipedia

A Flask web app that finds the shortest chain of links between any two Wikipedia articles. Enter a start and an end article, and it shows the chain of links that gets from one to the other. For example, **Peter Griffin → Assassination of Archduke Franz Ferdinand** takes 3 links: Peter Griffin → 68th Primetime Emmy Awards → Downton Abbey → Assassination of Archduke Franz Ferdinand. It finds this in about 5 seconds.

## Setup

You need Python 3 and Git.

**macOS**

```bash
git clone <repo-url>
cd six-degrees
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
git clone <repo-url>
cd six-degrees
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Replace `<repo-url>` with this repository's URL.

## Run

```bash
flask --app app run --port 5001
```

Then open <http://127.0.0.1:5001>.

The app uses port 5001 because macOS's AirPlay Receiver already uses port 5000.

## How it works

**Server (`app.py`, `wiki.py`)**
- Calls [Wikipedia's API](https://en.wikipedia.org/w/api.php), not the regular web pages, to:
  - look up article titles (following redirects, so "USA" becomes "United States");
  - get the links out of an article;
  - get the backlinks into an article.
- Runs a **bidirectional breadth-first search**. It searches forward from the start article using its links, and backward from the end article using its backlinks. Each round it expands whichever side currently has fewer articles waiting. It stops as soon as the two sides meet, and the result is still a shortest path.

**Browser (`templates/`)**
- The home page form is submitted with **GET**, so a search shows up in the URL (`/path?start=...&end=...`) and you can bookmark or share it.
- The results page shows the path as a numbered list linking to each Wikipedia article, plus the number of links, the articles checked and the time taken.

**Safety limits**
- At most **300 articles** fetched per search
- At most **60 seconds** per search
- At most **2,500 backlinks** per article
- **One request at a time**, each with a User-Agent naming the project and a contact email, and a 10-second timeout

## Error handling

| Situation | What the user sees |
|---|---|
| A box is left blank | "Please enter both articles." |
| Title doesn't exactly match an article (e.g. lowercase) | Uses Wikipedia's closest search match and shows "Showing results for X" |
| No matching article at all | "No Wikipedia article called X." |
| No path within the limits | "No path was found within the search limit." |
| No internet, a timeout, or a Wikipedia error | "Couldn't reach Wikipedia right now. Please try again." |
| Unknown URL | Custom 404 page |
| Unexpected bug | Custom 500 page (no Python traceback in the browser) |

## How I built it

I wrote the code with Claude in VS Code, adding one feature per prompt: the Wikipedia API functions, the search, the Flask pages, error handling, a faster bidirectional search, and polish. The prompts are in [PROMPTS.md](PROMPTS.md).

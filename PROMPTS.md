## Step 3: Wikipedia API functions

Create a file wiki.py for a Flask "Six Degrees of Wikipedia" project. Use the requests package and Wikipedia's API (https://en.wikipedia.org/w/api.php), not the web pages. Identify the program in the User-Agent header with the project name and my email, rconrad@scu.edu. Use a 10-second timeout on every request.

Write two functions:
1. resolve_title(title): returns the official article title, following redirects, or None if the article doesn't exist.
2. get_links(title): returns a list of all article titles linked from that article (main namespace only), handling Wikipedia's "continue" pagination so articles with more than 500 links are complete.

Don't touch app.py yet. Explain briefly how each function works.

## Step 4: Breadth-first search

In wiki.py, add a function find_path(start, end, max_articles=300) that uses breadth-first search to find the shortest chain of links from the start article to the end article, using get_links().

Requirements:
- Use a queue (collections.deque), a visited set, and a parent dictionary to rebuild the path at the end.
- Check whether a link is the end article as soon as you see it, instead of waiting until it comes off the queue.
- Count how many articles' links were fetched.
- Stop after max_articles fetches so it can't run forever.
- Return a dictionary: {"path": [list of titles] or None, "articles_checked": number}.
- If start and end are the same article, return the one-item path right away.

Don't touch app.py yet. After writing it, test it in Python with a close pair and a pair that's 2 links apart, and explain how the parent dictionary rebuilds the path.

## Step 5: Flask pages

Update app.py and add Jinja templates in a templates/ folder:

- base.html: shared layout with a page title, simple clean CSS inside a <style> tag, and a link back to the home page.
- index.html (route "/"): a short explanation of the app and a form with two text inputs, "start" and "end", and a "Find path" button. The form must use method GET and submit to /path. Pre-fill the example "Santa Clara University" and "Silicon Valley" as placeholders.
- result.html (route "/path"): read start and end from request.args, run both through resolve_title(), then call find_path(). Show the chain as a numbered list where each title links to its Wikipedia article (opens in a new tab), plus the number of articles checked and the time the search took in seconds. If no path was found within the limit, say so clearly.

Keep error handling minimal for now; I'll add it in the next step. Don't change wiki.py. Explain why the form uses GET.

## Step 6: Error handling

Add error handling so the app never shows a Python traceback in the browser:

1. In wiki.py, add search_title(query) that uses Wikipedia's API (opensearch or list=search, limit 1) to find the closest matching article title, or None. Use the same User-Agent and timeout.
2. In /path: if start or end is missing or blank, show the home page again with the message "Please enter both articles." If resolve_title() returns None, try search_title(). If that finds something, use it and show a note like "Showing results for X". If neither finds anything, show "No Wikipedia article called X."
3. Catch requests.exceptions.RequestException (timeouts, no internet, Wikipedia errors) around all Wikipedia calls and show "Couldn't reach Wikipedia right now. Please try again."
4. Add a custom 404 page (templates/404.html) and a custom 500 page (templates/500.html) using @app.errorhandler, both extending base.html with a link home.
5. Show error messages in a clearly styled box on the page, not as plain text.

Keep wiki.py functions small and reuse resolve_title(). Then test every case and list what each one shows.

## Step 7: Bidirectional search

The current find_path() is too slow: Peter Griffin → Assassination of Archduke Franz Ferdinand checked 300 articles in 117 seconds and found nothing. Replace it with a bidirectional breadth-first search in wiki.py:

1. Add get_backlinks(title, max_links=2500): uses list=backlinks (main namespace only) through api_get() and returns titles of articles that link TO the given article, following "continue" but stopping after max_links.
2. Rewrite find_path(start, end, max_articles=300, max_seconds=60) to search forward from start (using get_links) and backward from end (using get_backlinks) at the same time:
   - Keep a separate parent dictionary for each side.
   - Each round, expand one full layer of whichever side's frontier is smaller.
   - When an article appears in both sides, the searches have met. Finish the current layer and keep the meeting point that gives the shortest total path, so the result is still guaranteed shortest.
   - Rebuild the path: forward parents from start to the meeting article, then backward parents from the meeting article to end.
   - Stop when either max_articles fetches or max_seconds is reached.
   - Keep the same return format: {"path": [...] or None, "articles_checked": number}, counting fetches from both sides.
3. Make requests one at a time (no parallel requests) to stay polite to Wikipedia.

Keep app.py working without changes if possible. Test with SCU → Silicon Valley, SCU → Napoleon, and Peter Griffin → Assassination of Archduke Franz Ferdinand, and report the path, articles checked and seconds for each. Explain why expanding the smaller side first matters.
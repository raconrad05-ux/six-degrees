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
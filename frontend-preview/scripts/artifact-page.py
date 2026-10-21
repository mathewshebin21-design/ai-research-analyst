"""Turn the static export's index.html into a body fragment for hosts that supply
their own <html>/<head>/<body> skeleton (used for the hosted design preview)."""
import re
import sys

src, dest = sys.argv[1], sys.argv[2]
html = open(src, encoding="utf-8").read()
head = re.search(r"<head>(.*)</head>", html, re.S).group(1)
body = re.search(r"<body[^>]*>(.*)</body>", html, re.S).group(1)
head = re.sub(r'<meta charSet="utf-8"/>|<meta name="viewport"[^>]*/>', "", head)
title = re.search(r"<title>.*?</title>", head, re.S).group(0)
head = head.replace(title, "")
open(dest, "w", encoding="utf-8").write(
    title + '\n<meta name="claude:viewport-fit-sides" content="cover">\n' + head + "\n" + body
)

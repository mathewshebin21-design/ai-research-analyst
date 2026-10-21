"""Package the static export for hosts that supply their own <html>/<head>/<body>
skeleton and reserve top-level names starting with "_" (the hosted design preview).

Usage: PREVIEW_RELATIVE_ASSETS=1 npm run build && python scripts/artifact-page.py out dist-artifact
Writes dist-artifact/index.html (a body fragment) and dist-artifact/nx/ (the assets).
"""
import pathlib
import re
import shutil
import sys

src, dest = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
shutil.rmtree(dest, ignore_errors=True)
shutil.copytree(src / "_next", dest / "nx")

# Move assets from _next/ to nx/ and keep bundles plain ASCII-safe for the host's text checks.
for f in (dest / "nx").rglob("*"):
    if f.suffix in {".js", ".css"}:
        text = f.read_text(encoding="utf-8")
        f.write_text(text.replace("_next/", "nx/").replace("�", "\\uFFFD"), encoding="utf-8")

html = (src / "index.html").read_text(encoding="utf-8").replace("_next/", "nx/")
head = re.search(r"<head>(.*)</head>", html, re.S).group(1)
body = re.search(r"<body[^>]*>(.*)</body>", html, re.S).group(1)
head = re.sub(r'<meta charSet="utf-8"/>|<meta name="viewport"[^>]*/>|<link rel="icon"[^>]*/>', "", head)
title = re.search(r"<title>.*?</title>", head, re.S).group(0)
head = head.replace(title, "")
(dest / "index.html").write_text(
    title + '\n<meta name="claude:viewport-fit-sides" content="cover">\n' + head + "\n" + body, encoding="utf-8"
)

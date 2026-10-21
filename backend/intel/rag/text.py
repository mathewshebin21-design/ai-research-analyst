import re

_WS = re.compile(r"\s+")
_TOKEN = re.compile(r"[a-z0-9€$£%.,]+")
STOPWORDS = frozenset(
    "a an and are as at be by for from has have in is it its of on or that the this to was were will with "
    "which who what when where how than then into about over per their there these those not no but".split()
)


def normalize(text: str) -> str:
    return _WS.sub(" ", text).strip()


def tokens(text: str) -> list[str]:
    out = []
    for t in _TOKEN.findall(text.lower()):
        t = t.strip(".,")
        if t and t not in STOPWORDS:
            out.append(t)
    return out


def split_passages(text: str, target: int = 900, overlap: int = 150) -> list[str]:
    """Split on paragraph and sentence boundaries into passages of about `target` characters."""
    text = text.replace("\r", "")
    paras = [normalize(p) for p in re.split(r"\n\s*\n", text) if normalize(p)]
    units: list[str] = []
    for p in paras:
        if len(p) <= target:
            units.append(p)
        else:
            units.extend(s for s in re.split(r"(?<=[.!?])\s+", p) if s)
    passages: list[str] = []
    cur = ""
    for u in units:
        if cur and len(cur) + len(u) + 1 > target:
            passages.append(cur)
            cur = cur[-overlap:].split(" ", 1)[-1] + " " + u if overlap else u
        else:
            cur = f"{cur} {u}".strip()
    if cur:
        passages.append(cur)
    # Hard-split anything still oversized (e.g. text without punctuation).
    final: list[str] = []
    for p in passages:
        while len(p) > target * 2:
            final.append(p[:target])
            p = p[target - overlap :]
        final.append(p)
    return final


def find_quote(passage: str, quote: str) -> tuple[int, int] | None:
    """Locate a verifier quote in a passage, tolerating whitespace and quote-mark differences only."""
    if not quote or len(quote.strip()) < 8:
        return None
    exact = passage.find(quote)
    if exact >= 0:
        return exact, exact + len(quote)

    def canon(s: str) -> str:
        return s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')

    # Map normalized-passage positions back to original positions.
    p = canon(passage)
    q = normalize(canon(quote))
    chars: list[str] = []
    index: list[int] = []
    prev_space = False
    for i, ch in enumerate(p):
        if ch.isspace():
            if prev_space or not chars:
                continue
            chars.append(" ")
            index.append(i)
            prev_space = True
        else:
            chars.append(ch)
            index.append(i)
            prev_space = False
    flat = "".join(chars)
    at = flat.find(q)
    if at < 0:
        return None
    return index[at], index[at + len(q) - 1] + 1

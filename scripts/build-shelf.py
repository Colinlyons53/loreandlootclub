"""Rebuild the shelf list, filter counts and home page teaser from data/shelf.json.

Run from the repo root: python3 scripts/build-shelf.py
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENRES = {"litrpg": "LitRPG and progression", "fantasy": "Fantasy", "scifi": "Sci-fi",
          "drama": "Full-cast audio", "comics": "Comics"}

items = json.loads((ROOT / "data/shelf.json").read_text())
order = list(GENRES)
items.sort(key=lambda s: (order.index(s["genre"]), -s["count"]))
n_series, n_books = len(items), sum(s["count"] for s in items)
e = html.escape

rows = []
for s in items:
    by = e(s["author"]) + (f'<span class="s-narr">, read by {e(s["narrator"])}</span>' if s["narrator"] and s["narrator"] != "full cast"
                           else ', full cast' if s["narrator"] == "full cast" else "")
    rows.append(f'''      <li data-genre="{s["genre"]}">
        <span class="s-name">{e(s["series"])}</span>
        <span class="s-by">{by}</span>
        <span class="s-count">{e(s["books"])}</span>
      </li>''')

chips = [f'      <button type="button" class="chip" data-filter="all" aria-pressed="true">All <span>{n_series}</span></button>']
chips += [f'      <button type="button" class="chip" data-filter="{k}" aria-pressed="false">{v} <span>{sum(1 for s in items if s["genre"] == k)}</span></button>'
          for k, v in GENRES.items()]

ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "The Shelf",
      "url": "https://loreandlootclub.com/shelf", "numberOfItems": n_series,
      "itemListElement": [{"@type": "ListItem", "position": i + 1,
                           "item": {"@type": "BookSeries", "name": s["series"],
                                    "author": {"@type": "Person", "name": s["author"]}}}
                          for i, s in enumerate(items)]}

page = ROOT / "public/shelf.html"
p = page.read_text()
p = re.sub(r'(<ul class="series" id="shelf">\n).*?(\n  </ul>)', lambda m: m.group(1) + "\n".join(rows) + m.group(2), p, flags=re.S)
p = re.sub(r'(<div class="chips"[^>]*>\n).*?(\n    </div>)', lambda m: m.group(1) + "\n".join(chips) + m.group(2), p, flags=re.S)
p = re.sub(r'(<script type="application/ld\+json">\n).*?(\n</script>)', lambda m: m.group(1) + json.dumps(ld, indent=1, ensure_ascii=False) + m.group(2), p, flags=re.S)
p = re.sub(r'<p class="lede">.*?</p>', f'<p class="lede">Complete series worth checking out, by audiobook and on Kindle. {n_series} series and about {n_books} books so far, grouped by genre with the longest runs first.</p>', p, count=1, flags=re.S)
desc = f"Complete LitRPG, fantasy and sci-fi series worth checking out, {n_series} series in all, from The Wandering Inn and Cradle to Dune and The Lord of the Rings."
p = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', p)
p = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{desc}">', p)
favs = [x for x in items if x.get("favorite")]
fav_html = "\n".join(f'''      <li>
        <span class="fav-name">{e(x["series"])}</span>
        <span class="fav-by">{e(x["author"])}, {e(x["books"])}</span>
        <p>{e(x["favorite"])}</p>
      </li>''' for x in favs)
p = re.sub(r'(<ul class="fav-list">\n).*?(\n?    </ul>)', lambda m: m.group(1) + fav_html + "\n    </ul>", p, flags=re.S)
page.write_text(p)

# Bundles page
def hours(length):
    h = re.search(r"(\d+) hrs?", length); m = re.search(r"(\d+) mins?", length)
    return int(h.group(1) if h else 0) + int(m.group(1) if m else 0) / 60
bundles = sorted(json.loads((ROOT / "data/bundles.json").read_text()), key=lambda b: -hours(b["length"]))
b_rows = "\n".join(f'''    <li>
      <div class="b-main">
        <span class="b-title">{e(b["title"])}</span>
        <span class="b-by">{e(b["author"])}, read by {e(b["narrator"])}. {e(b["contains"])}.</span>
      </div>
      <span class="b-genre">{e(b["genre"])}</span>
      <span class="b-len">{e(b["length"])}</span>
      <a class="b-link" href="{e(b["url"])}" rel="noopener">On Audible<span class="sr">: {e(b["title"])}</span></a>
    </li>''' for b in bundles)
bld = {"@context": "https://schema.org", "@type": "ItemList", "name": "Best value Audible bundles",
       "url": "https://loreandlootclub.com/bundles", "numberOfItems": len(bundles),
       "itemListElement": [{"@type": "ListItem", "position": i + 1,
                            "item": {"@type": "Audiobook", "name": b["title"], "url": b["url"],
                                     "author": {"@type": "Person", "name": b["author"]},
                                     "readBy": {"@type": "Person", "name": b["narrator"]}}}
                           for i, b in enumerate(bundles)]}
bp = ROOT / "public/bundles.html"
q = bp.read_text()
q = re.sub(r'(<ol class="bundles" id="bundles">\n).*?(\n?  </ol>)', lambda m: m.group(1) + b_rows + "\n  </ol>", q, flags=re.S)
q = re.sub(r'(<script type="application/ld\+json">\n).*?(\n</script>)', lambda m: m.group(1) + json.dumps(bld, indent=1, ensure_ascii=False) + m.group(2), q, flags=re.S)
bp.write_text(q)

home = ROOT / "public/index.html"
h = home.read_text()
h = re.sub(r'<a href="/shelf">\d+ series finished</a>', f'<a href="/shelf">{n_series} series finished</a>', h)
h = re.sub(r'About \d+ books, from all 19.*?</p>', f'About {n_books} books, from all 19 of The Wandering Inn and all 14 of The Wheel of Time to Dune and The Lord of the Rings, plus full-cast zombie audio drama. Filter it by genre or search for something you\'ve read.</p>', h, flags=re.S)
home.write_text(h)

llms = ROOT / "public/llms.txt"
l = llms.read_text()
l = re.sub(r'- \[Shelf\]\(https://loreandlootclub.com/shelf\): .*', f'- [Shelf](https://loreandlootclub.com/shelf): complete LitRPG, fantasy, sci-fi, full-cast audio drama and comic series worth checking out, {n_series} series and about {n_books} books', l)
llms.write_text(l)
print(n_series, "series,", n_books, "books")

#!/usr/bin/env python3
"""Every cited item has a recorded verification, and every quotation is in the abstract it quotes.

1. The keys cited in the paper, the keys quoted with \\srcq, the \\bibitem keys and the items of literature/sources.json
   are the same set: nothing is cited without a record, and nothing is recorded without being cited.
2. Each item has a read mode from the fixed list, a DOI, and a stored Crossref record (literature/crossref/) whose DOI
   is that DOI. Items read as "abstract-openalex" also have a stored OpenAlex record (literature/openalex/) whose
   abstract is the one rebuilt from its index of word positions.
3. Each \\bibitem carries the DOI of its item, and agrees with the stored Crossref record on the year, the title and the
   first author's family name. Entries give only authors, year, title and DOI (no journal, publisher or pages), since the
   paper names no organisation; check_text.py checks that.
4. Each quotation \\srcq{key}{text} is from an item read as an abstract, and the text occurs in that abstract.
5. The table of Section "Literature, and how each item was read" gives each item the read mode recorded for it.
6. With --online, the Crossref record of every DOI is fetched again and compared with the stored one (title, year, DOI).

  python3 verification/check_sources.py            # the check
  python3 verification/check_sources.py --online   # the check, and a fresh comparison with Crossref
  python3 verification/check_sources.py --break    # each change made in memory must fail
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paperlib import ROOT, TEX, read, srcq, cite_keys, bibitems, norm  # noqa: E402

# The paper names no organisation (the user's rule of 2026-11-23), so its table describes the sources of the abstracts
# generically: the DOI record (Crossref) and the bibliographic index (OpenAlex).
MODES = {"abstract-crossref": "abstract (DOI record)", "abstract-openalex": "abstract (bibliographic index)",
         "record": "record only"}


def load():
    src = json.loads(read("literature/sources.json"))
    cr, oa = {}, {}
    for it in src["items"]:
        p = os.path.join(ROOT, it.get("crossref", ""))
        cr[it["key"]] = json.load(open(p, encoding="utf-8")) if it.get("crossref") and os.path.exists(p) else None
        if it.get("openalex"):
            q = os.path.join(ROOT, it["openalex"])
            oa[it["key"]] = json.load(open(q, encoding="utf-8")) if os.path.exists(q) else None
    return {"tex": read(TEX), "src": src, "cr": cr, "oa": oa}


def rebuild(inv):
    pos = {p: w for w, ps in (inv or {}).items() for p in ps}
    return " ".join(pos[i] for i in sorted(pos))


def abstract_of(x, key, mode):
    if mode == "abstract-crossref":
        return norm((x["cr"].get(key) or {}).get("abstract", ""))
    if mode == "abstract-openalex":
        return norm((x["oa"].get(key) or {}).get("abstract", ""))
    return ""


def flat(s):
    s = re.sub(r"\\emph\{([^{}]*)\}|<i>(.*?)</i>", lambda m: m.group(1) or m.group(2) or "", s)
    s = s.replace("\\&", "&").replace("---", "\u2014").replace("--", "-").replace("~", " ").replace("'", "\u2019")
    return re.sub(r"[^0-9a-z]+", " ", s.lower().replace("\u2019", "")).strip()


def problems(x):
    bad = []
    items = {it["key"]: it for it in x["src"]["items"]}
    tex = x["tex"]
    cited, quoted, bib = set(cite_keys(tex)), {k for k, _ in srcq(tex)}, bibitems(tex)
    for k in sorted((cited | quoted) - set(bib)):
        bad.append(f"{k}: cited or quoted but has no \\bibitem")
    for k in sorted(set(bib) - cited):
        bad.append(f"{k}: in the bibliography but never cited")
    for k in sorted(set(bib) ^ set(items)):
        bad.append(f"{k}: in only one of the bibliography and literature/sources.json")
    for k, it in items.items():
        if it.get("read") not in MODES:
            bad.append(f"{k}: read mode {it.get('read')!r} is not one of {sorted(MODES)}")
        rec = x["cr"].get(k)
        if not rec:
            bad.append(f"{k}: no stored Crossref record")
            continue
        if rec.get("DOI", "").lower() != it.get("doi", "").lower():
            bad.append(f"{k}: the stored Crossref record is for {rec.get('DOI')}, not {it.get('doi')}")
        if it.get("read") == "abstract-crossref" and not rec.get("abstract"):
            bad.append(f"{k}: read as a Crossref abstract, but the stored record has none")
        if it.get("read") == "abstract-openalex":
            o = x["oa"].get(k)
            if not o or not o.get("abstract") or o["abstract"] != rebuild(o.get("abstract_inverted_index")):
                bad.append(f"{k}: the stored OpenAlex abstract is missing or is not the one rebuilt from its index")
            elif (o.get("doi") or "").lower() != "https://doi.org/" + it["doi"].lower():
                bad.append(f"{k}: the stored OpenAlex record is for another DOI")
        b = bib.get(k, "")
        if b:
            d = re.search(r"\\doi\{([^{}]+)\}", b)
            if not d or d.group(1).lower() != it.get("doi", "").lower():
                bad.append(f"{k}: the \\bibitem does not carry the DOI {it.get('doi')}")
            year = str(((rec.get("issued") or {}).get("date-parts") or [[None]])[0][0])
            if f"({year}" not in b:
                bad.append(f"{k}: the \\bibitem year is not the record's {year}")
            title = flat((rec.get("title") or [""])[0])
            if title and title not in flat(b):
                bad.append(f"{k}: the \\bibitem title is not the record's title")
            people = rec.get("author") or [a for a in rec.get("editor", []) if a.get("family")] or []
            fam = (people[0].get("family") or people[0].get("name") or "") if people else ""
            if fam and flat(fam) not in flat(b):
                bad.append(f"{k}: the \\bibitem lacks the first author {fam}")
    for k, q in srcq(tex):
        it = items.get(k)
        if not it:
            continue
        if it.get("read") not in ("abstract-crossref", "abstract-openalex"):
            bad.append(f"{k}: quoted, but read as {it.get('read')}")
        elif norm(q) not in abstract_of(x, k, it["read"]):
            bad.append(f"{k}: quotation not in the stored abstract: {q[:60]}")
    lit = tex[tex.find(r"\section{Literature, and how each item was read}"):]
    for k, it in items.items():
        m = re.search(r"\\citet\{" + re.escape(k) + r"\} & ([^&]+?) &", lit)
        if not m:
            bad.append(f"{k}: no row in the literature table")
        elif m.group(1).strip() != MODES.get(it.get("read")):
            bad.append(f"{k}: the literature table says '{m.group(1).strip()}', the record says {it.get('read')}")
    return bad


def online(x):
    import time
    import urllib.parse
    import urllib.request
    bad = []
    for it in x["src"]["items"]:
        url = "https://api.crossref.org/works/" + urllib.parse.quote(it["doi"])
        m = None
        for k in range(5):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "boys-school-philosophy-check/1.0"})
                m = json.load(urllib.request.urlopen(req, timeout=60))["message"]
                break
            except Exception:
                time.sleep(5 * (k + 1))
        s = x["cr"].get(it["key"]) or {}
        if m is None:
            bad.append(f"{it['key']}: Crossref did not answer")
            continue
        for f in ("DOI", "title", "issued"):
            if (m.get(f).lower() if f == "DOI" else m.get(f)) != (s.get(f).lower() if f == "DOI" and s.get(f) else s.get(f)):
                bad.append(f"{it['key']}: Crossref's {f} now differs from the stored record")
        time.sleep(1)
    return bad


def breaks(x):
    def tex(a, b):
        y = dict(x)
        assert a in x["tex"], a
        y["tex"] = x["tex"].replace(a, b, 1)
        return y

    def src(f):
        y = dict(x)
        y["src"] = json.loads(json.dumps(x["src"]))
        f(y["src"])
        return y

    def oa(k, f):
        y = dict(x)
        y["oa"] = json.loads(json.dumps(x["oa"]))
        f(y["oa"][k])
        return y

    def item(k):
        return lambda s: next(i for i in s["items"] if i["key"] == k)
    return [
        ("a citation with no record", tex(r"\citet{booth2011} randomly", r"\citet{booth2012} randomly")),
        ("an item recorded but not cited", src(lambda s: s["items"].append(dict(s["items"][0], key="extra2026")))),
        ("an item without a read mode", src(lambda s: item("doris2012")(s).update(read="skimmed"))),
        ("a DOI changed in the bibliography", tex(r"\doi{10.2139/ssrn.2164646}", r"\doi{10.2139/ssrn.2164647}")),
        ("a year changed in the bibliography", tex(r"Sullivan, A., Joshi, H., \& Leonard, D. (2010)", r"Sullivan, A., Joshi, H., \& Leonard, D. (2011)")),
        ("a first author changed in the bibliography", tex("Doris, A., O'Neill", "Dorris, A., O'Neill")),
        ("a title changed in the bibliography", tex("Why are single-sex schools successful?", "Why are single-sex schools unsuccessful?")),
        ("a quotation changed by one word", tex("only trivial differences between students", "no differences between students")),
        ("a quotation from an item read only as a record", tex(r"reviewing \citet{salomone2017},", r"reviewing \citet{salomone2017}, \srcq{salomone2017}{Same, Different, Equal},")),
        ("a quotation attributed to the wrong item", tex(r"\srcq{lee2021}{the effect of single-sex schooling on earnings", r"\srcq{leenakazawa2021}{the effect of single-sex schooling on earnings")),
        ("the OpenAlex abstract edited without its index", oa("pahlke2014", lambda o: o.update(abstract=o["abstract"].replace("184", "185")))),
        ("the literature table changes a read mode", tex(r"\citet{salomone2017} & record only", r"\citet{salomone2017} & abstract (DOI record)")),
        ("a read mode changed in sources.json only", src(lambda s: item("halpern2011")(s).update(read="abstract-openalex"))),
    ]


def main(argv):
    x = load()
    if "--break" in argv:
        if problems(x):
            print("break test: the unbroken state already fails")
            return 1
        missed = 0
        for what, y in breaks(x):
            caught = bool(problems(y))
            print(f"  {'caught' if caught else 'MISSED'}: {what}")
            missed += not caught
        print("break test: " + ("every change made the check fail, as it should" if not missed else f"{missed} missed"))
        return 1 if missed else 0
    bad = problems(x)
    if "--online" in argv:
        bad += online(x)
    n = len(x["src"]["items"])
    print(f"sources: {n} items, {len(srcq(x['tex']))} quotations, {len(bad)} problems")
    for b in bad:
        print("  " + b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Shared helpers for the checks: paths, the LaTeX source split into parts, and the text of the PDF."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = "paper/boys-school-philosophy.tex"
PDF = "paper/boys-school-philosophy.pdf"
TITLE = "The Philosophical Value of Public Boys' Schools"
TITLE_JA = "公立男子校の哲学的価値"
AUTHOR = "Takuya Nemoto"
ORCID = "0009-0000-1406-0547"


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def uncomment(tex):
    """Drops LaTeX comments (an unescaped % to the end of the line)."""
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in tex.split("\n"))


def body(tex):
    """The text between \\begin{document} and the bibliography, without comments."""
    t = uncomment(tex)
    i, j = t.find(r"\begin{document}"), t.find(r"\begin{thebibliography}")
    return t[i:j] if i >= 0 and j > i else ""


def srcq(tex):
    """Every quotation from a source: (key, quoted text). The macro is \\srcq{key}{text}; text has no braces."""
    return re.findall(r"\\srcq\{([^{}]+)\}\{([^{}]*)\}", uncomment(tex))


def cite_keys(tex):
    keys = []
    for m in re.finditer(r"\\cite[tp]?\*?(?:\[[^\]]*\])*\{([^{}]+)\}", uncomment(tex)):
        keys += [k.strip() for k in m.group(1).split(",")]
    return keys


def bibitems(tex):
    """key -> the text of its \\bibitem entry."""
    t = uncomment(tex)
    i, j = t.find(r"\begin{thebibliography}"), t.find(r"\end{thebibliography}")
    out = {}
    for m in re.finditer(r"\\bibitem\[[^\]]*\]\{([^{}]+)\}(.*?)(?=\\bibitem|\Z)", t[i:j], re.S):
        out[m.group(1)] = m.group(2).strip()
    return out


def pdf_text(rel=PDF):
    import pypdf
    r = pypdf.PdfReader(os.path.join(ROOT, rel))
    return r, "\n".join(p.extract_text() or "" for p in r.pages)


def word_count(text):
    """Words of the paper's body in the PDF text: from the heading "1 Introduction" to the heading of the
    disclosure of the use of a language model. A word is a run of non-space characters with a Latin letter or a digit."""
    i = text.find("1 Introduction")
    j = text.find("Disclosure of the use of a language model", i)
    if i < 0 or j < 0:
        return None
    return len(re.findall(r"\S*[A-Za-z0-9]\S*", text[i:j]))


def norm(s):
    """For comparing a quotation with an abstract: LaTeX quotes and dashes to plain forms, one space."""
    s = s.replace("``", '"').replace("''", '"').replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("---", "\u2014").replace("--", "\u2013").replace("~", " ").replace("\\&", "&")
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()

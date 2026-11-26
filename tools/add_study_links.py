#!/usr/bin/env python3
"""
Adds a small, honest "Related study material" box to every guide (only the 1-3 courses that match
the guide's topic) and builds guides/study-material.html (class-wise hub).
Run from the repo root:   python tools/add_study_links.py
Safe to run again: the box is wrapped in markers and replaced, never duplicated.
Edit tools/courses.json (title, classes, semester, url, kw = keywords) when you add a course.
"""
import json, re, html, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ROOT / "guides"
COURSES = json.loads((Path(__file__).parent / "courses.json").read_text(encoding="utf-8"))
ALL_URL = "https://lms.universitygyaan.in/courses"
B, E = "<!--ug-study-start-->", "<!--ug-study-end-->"
CSS_MARK = "/* ug-study */"
CSS = CSS_MARK + """
.ug-study{margin:28px 0 8px;padding:16px 18px;border:1px solid rgba(0,0,0,.12);border-radius:14px;background:#f6f8ff}
.ug-study h2{margin:0 0 4px;font-size:1.05rem}
.ug-study p{margin:0 0 10px;font-size:.9rem;opacity:.8}
.ug-study ul{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.ug-study li a{display:block;padding:10px 12px;border-radius:10px;background:#fff;border:1px solid rgba(0,0,0,.1);text-decoration:none;font-weight:600}
.ug-study li a small{display:block;font-weight:400;opacity:.7;margin-top:2px}
.ug-study .more{margin-top:10px;font-size:.9rem}
"""

def esc(s): return html.escape(s, quote=True)

def text_of(src):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", src, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", t).lower()

def match(src):
    title = (re.search(r"<title>(.*?)</title>", src, re.S | re.I) or [None, ""])[1].lower()
    h1 = (re.search(r"<h1[^>]*>(.*?)</h1>", src, re.S | re.I) or [None, ""])[1].lower()
    body = text_of(src)
    scored = []
    for c in COURSES:
        s = 0
        for k in c["kw"]:
            k = k.lower()
            if k in title or k in h1: s += 5
            s += min(body.count(k), 3)
        if s >= 5: scored.append((s, c))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:3]]

def label(c):
    return " · ".join([x for x in [", ".join(c["classes"]), c["semester"]] if x])

def box(cs):
    items = "".join(
        f'<li><a href="{esc(c["url"])}" rel="noopener">{esc(c["title"])}<small>{esc(label(c))}</small></a></li>' for c in cs)
    lead = ("University Gyaan ke study material (notes, MCQ, PYQ) jo is topic se jude hain. "
            "Ye hamare apne LMS ke links hain; guide padhne ke liye inki zaroorat nahi hai.") if cs else \
           "University Gyaan ke saare course aur study material ek jagah dekhne ke liye."
    body = f"<ul>{items}</ul>" if cs else ""
    return (f'{B}<aside class="ug-study" aria-label="Related study material"><h2>Related study material</h2>'
            f'<p>{lead}</p>{body}<p class="more"><a href="study-material.html">Class ke hisaab se sab course dekhein →</a></p></aside>{E}')

def inject(src, b):
    src = re.sub(re.escape(B) + r".*?" + re.escape(E), "", src, flags=re.S)
    for pat in (r"</article>", r"</main>", r"<footer"):
        m = list(re.finditer(pat, src, re.I))
        if m:
            i = m[-1].start()
            return src[:i] + b + "\n" + src[i:]
    return src.replace("</body>", b + "</body>", 1)

def hub_page(template):
    src = template.read_text(encoding="utf-8")
    groups = {}
    for c in COURSES:
        for cl in (c["classes"] or ["Other"]): groups.setdefault(cl, []).append(c)
    secs = ""
    for cl in sorted(groups):
        li = "".join(f'<li><a href="{esc(c["url"])}" rel="noopener">{esc(c["title"])}<small>{esc(label(c))}</small></a></li>' for c in groups[cl])
        secs += f"<h2>{esc(cl)}</h2><ul class=\"ug-hub\">{li}</ul>"
    inner = ("<h1>Study Material by Class</h1>"
             "<p>University Gyaan ke LMS par har class ke liye PDF notes, MCQ tests aur previous year questions alag course me rakhe gaye hain. "
             "Har course ka free preview dekha ja sakta hai, aur bahut se guides is site par bina kisi shulk ke padhe ja sakte hain.</p>"
             + secs +
             f'<p><a href="{ALL_URL}" rel="noopener">Saare courses LMS par dekhein →</a></p>')
    for tag in ("main", "article"):
        m = re.search(rf"(<{tag}[^>]*>).*?(</{tag}>)", src, re.S | re.I)
        if m:
            src = src[:m.start()] + m.group(1) + inner + m.group(2) + src[m.end():]
            break
    else:
        return None
    src = re.sub(r"<title>.*?</title>", "<title>Study Material by Class | University Gyaan</title>", src, flags=re.S | re.I)
    src = re.sub(r'(<meta\s+name="description"\s+content=")[^"]*', r"\1Class-wise list of University Gyaan study material courses: notes, MCQ and PYQ.", src, flags=re.I)
    src = re.sub(r'<link\s+rel="canonical"[^>]*>', '<link rel="canonical" href="https://universitygyaan.in/guides/study-material.html">', src, flags=re.I)
    src = re.sub(r'<script type="application/ld\+json">.*?</script>', "", src, flags=re.S | re.I)
    src = re.sub(re.escape(B) + r".*?" + re.escape(E), "", src, flags=re.S)
    return src

def main():
    if not GUIDES.is_dir(): sys.exit("guides/ folder nahi mila - repo root se chalayein.")
    files = [p for p in sorted(GUIDES.glob("*.html")) if p.name not in ("index.html", "study-material.html")]
    for p in files:
        src = p.read_text(encoding="utf-8")
        cs = match(src)
        p.write_text(inject(src, box(cs)), encoding="utf-8")
        print(f"{p.name}: {', '.join(c['title'] for c in cs) or '(sirf all-courses link)'}")
    css = GUIDES / "guide.css"
    if css.exists() and CSS_MARK not in css.read_text(encoding="utf-8"):
        css.write_text(css.read_text(encoding="utf-8") + "\n" + CSS, encoding="utf-8")
    tpl = GUIDES / "index.html"
    out = hub_page(tpl) if tpl.exists() else None
    if out:
        (GUIDES / "study-material.html").write_text(out, encoding="utf-8")
        print("study-material.html ban gaya")
        sm = ROOT / "sitemap.xml"
        if sm.exists():
            s = sm.read_text(encoding="utf-8")
            if "study-material.html" not in s:
                s = s.replace("</urlset>", "  <url><loc>https://universitygyaan.in/guides/study-material.html</loc></url>\n</urlset>")
                sm.write_text(s, encoding="utf-8")
    else:
        print("Hub page nahi bana (guides/index.html me <main> ya <article> nahi mila).")

main()

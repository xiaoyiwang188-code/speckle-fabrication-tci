"""CrossRef verification of all 12 bib entries. Prints per-entry verdict to stdout.
Usage: python verify_all_refs.py   (run from paper/)

Security: only https requests to the fixed api.crossref.org host are permitted;
DOIs are URL-path-encoded, and any redirect off the allowlisted host is rejected.
"""
import re, time, json, ipaddress, socket, urllib.request, urllib.parse

ALLOWED_HOSTS = {"api.crossref.org"}
ALLOWED_SCHEMES = {"https"}

def check_url(url):
    p = urllib.parse.urlparse(url)
    if p.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"scheme not allowed: {p.scheme}")
    if p.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"host not allowlisted: {p.hostname}")
    for ip in socket.getaddrinfo(p.hostname, 443, proto=socket.IPPROTO_TCP):
        addr = ip[4][0]
        if not ipaddress.ip_address(addr).is_global:
            raise ValueError(f"non-global address for {p.hostname}: {addr}")
    return url

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError(f"redirect rejected: {newurl}")

BIB = open("references.bib", encoding="utf-8").read()
# split on the entry-opening marker so the LAST field of each entry is retained
chunks = re.split(r"\n(?=@)", BIB.strip())
entries = []
for ch in chunks:
    m = re.match(r"@(\w+)\{([^,]+),", ch)
    if m:
        entries.append((m.group(1), m.group(2), ch[m.end():]))
print(f"entries parsed: {len(entries)}")

def field(body, name):
    m = re.search(name + r"\s*=\s*\{(.*?)\}\s*,?\s*\n", body, re.S)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(name + r"\s*=\s*(\S+)\s*,?\s*\n", body)
    return m.group(1).strip(",") if m else None

def crossref(doi):
    url = check_url(f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}")
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": "paper-verify/1.0 (mailto:research@example.org)"})
    with opener.open(req, timeout=40) as r:
        return json.load(r)["message"]

def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).replace("\\", "").strip()

results = []
for etype, key, body in entries:
    doi = field(body, "doi")
    title = field(body, "title")
    venue = field(body, "journal") or field(body, "booktitle") or ""
    if not doi:
        results.append((key, "NO_DOI", "-", "-"))
        continue
    d = None
    for attempt in range(3):
        try:
            d = crossref(doi)
            break
        except Exception as e:
            if attempt == 2:
                results.append((key, f"LOOKUP_FAIL: {type(e).__name__} {str(e)[:40]}", "-", doi))
            time.sleep(20)
    if d is None:
        continue
    cr_authors = [f"{a.get('family','')}, {a.get('given','')}".strip(", ")
                  for a in d.get("author", [])]
    bib_authors = [a.strip() for a in re.split(r"\s+and\s+", field(body, "author") or "")]
    cr_year = str((d.get("issued", {}).get("date-parts") or [[None]])[0][0])
    bib_year = (field(body, "year") or "").strip("{}")
    cr_title = (d.get("title") or ["?"])[0]
    cr_venue = (d.get("container-title") or ["?"])[0]
    issues = []
    if len(cr_authors) != len(bib_authors):
        issues.append(f"n_authors bib={len(bib_authors)} cr={len(cr_authors)}")
    else:
        for i in range(min(2, len(cr_authors))):
            if norm(cr_authors[i].split(",")[0]) not in norm(bib_authors[i]):
                issues.append(f"author[{i}] cr='{cr_authors[i]}' vs bib='{bib_authors[i]}'")
    if bib_year and cr_year and bib_year != cr_year:
        issues.append(f"year {bib_year}!={cr_year}")
    if norm(title) and norm(cr_title) and norm(title)[:40] != norm(cr_title)[:40]:
        issues.append(f"title: '{title[:45]}' vs '{cr_title[:45]}'")
    if norm(venue) and norm(cr_venue) and norm(venue)[:20] != norm(cr_venue)[:20]:
        issues.append(f"venue '{venue}' vs '{cr_venue}'")
    verdict = "OK" if not issues else "CHECK: " + " | ".join(issues)
    results.append((key, verdict, cr_venue, cr_year))
    print(f"{key}: {verdict}")
    time.sleep(1)

print("\nSUMMARY")
n_ok = sum(1 for r in results if r[1] == "OK")
for k, v, ven, yr in results:
    if v != "OK":
        print(f"  {k}: {v}")
print(f"{n_ok}/{len(results)} entries clean")

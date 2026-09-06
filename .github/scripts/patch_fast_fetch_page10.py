from pathlib import Path

p = Path("commonlib/src/pouchdb/StreamingFetch.ts")
s = p.read_text()
old = "        const pageSize = 50;"
new = "        const pageSize = 10;"
if old not in s:
    raise SystemExit("Fast Fetch page-size 50 anchor not found")
p.write_text(s.replace(old, new, 1))
print("Fast Fetch page size reduced from 50 to 10")

from pathlib import Path

p = Path("commonlib/src/pouchdb/StreamingFetch.ts")
s = p.read_text()

old = '''    let totalFetched = 0;
    let totalValidFetched = 0;
    let totalBytes = 0;
'''
new = '''    let totalFetched = 0;
    let totalValidFetched = 0;
    let totalBytes = 0;
    const localDocCountAtStart = (await downloadToDB.info()).doc_count;
    Logger(`[FastFetchProgress] start local=${localDocCountAtStart} downloaded=0 remaining=unknown`);
'''
if old not in s:
    raise SystemExit("progress start anchor not found")
s = s.replace(old, new, 1)

old = '''        while (true) {
            const pageStartedAt = Date.now();
            let page;
'''
new = '''        while (true) {
            const remainingBefore = docsToFetch > 0 ? Math.max(0, docsToFetch - totalFetched) : "unknown";
            Logger(
                `[FastFetchProgress] requesting page=${pageSize} local≈${localDocCountAtStart + totalValidFetched} downloaded=${totalFetched} valid=${totalValidFetched} remaining≈${remainingBefore}`
            );
            const pageStartedAt = Date.now();
            let page;
'''
if old not in s:
    raise SystemExit("progress request anchor not found")
s = s.replace(old, new, 1)

old = '''                    Logger(
                        `[FastFetchDebug] adaptive page fetch failed; reducing page size ${previousPageSize} -> ${pageSize}`
                    );
                    continue;
'''
new = '''                    Logger(
                        `[FastFetchDebug] adaptive page fetch failed; reducing page size ${previousPageSize} -> ${pageSize}`
                    );
                    Logger(
                        `[FastFetchProgress] page failed; downloaded=${totalFetched} local≈${localDocCountAtStart + totalValidFetched} nextPage=${pageSize}`
                    );
                    continue;
'''
if old not in s:
    raise SystemExit("progress failure anchor not found")
s = s.replace(old, new, 1)

old = '''            pageSince = page.lastSequence;
            docsToFetch = Math.max(docsToFetch, totalFetched + page.pending);

            if (page.rowCount > 0 && !started) {
'''
new = '''            pageSince = page.lastSequence;
            docsToFetch = Math.max(docsToFetch, totalFetched + page.pending);
            Logger(
                `[FastFetchProgress] downloaded=${totalFetched} valid=${totalValidFetched} local≈${localDocCountAtStart + totalValidFetched} remaining≈${page.pending} total≈${totalFetched + page.pending} page=${pageSize}`
            );

            if (page.rowCount > 0 && !started) {
'''
if old not in s:
    raise SystemExit("progress success anchor not found")
s = s.replace(old, new, 1)

p.write_text(s)
print("Fast Fetch visible document progress logging applied")

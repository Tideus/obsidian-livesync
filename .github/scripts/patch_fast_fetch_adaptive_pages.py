from pathlib import Path

p = Path("commonlib/src/pouchdb/StreamingFetch.ts")
s = p.read_text()

old = '''        const pageSize = 10;

        while (true) {
            const page = await fetchPageNormal(pageSince, pageSize);
            pageSince = page.lastSequence;
            docsToFetch = Math.max(docsToFetch, totalFetched + page.pending);
'''

new = '''        let pageSize = 10;
        let fastPageStreak = 0;
        const minPageSize = 5;
        const maxPageSize = 10;

        while (true) {
            const pageStartedAt = Date.now();
            let page;
            try {
                page = await fetchPageNormal(pageSince, pageSize);
            } catch (error) {
                if (pageSize > minPageSize) {
                    const previousPageSize = pageSize;
                    pageSize = minPageSize;
                    fastPageStreak = 0;
                    Logger(
                        `[FastFetchDebug] adaptive page fetch failed; reducing page size ${previousPageSize} -> ${pageSize}`
                    );
                    continue;
                }
                throw error;
            }

            const pageElapsedMs = Date.now() - pageStartedAt;
            Logger(
                `[FastFetchDebug] adaptive page completed size=${pageSize} rows=${page.rowCount} elapsed=${pageElapsedMs}ms pending=${page.pending}`
            );

            if (pageElapsedMs <= 2000 && page.rowCount >= pageSize && page.pending > 0) {
                fastPageStreak++;
                if (fastPageStreak >= 3 && pageSize < maxPageSize) {
                    const previousPageSize = pageSize;
                    pageSize = maxPageSize;
                    fastPageStreak = 0;
                    Logger(
                        `[FastFetchDebug] adaptive page size increased ${previousPageSize} -> ${pageSize}`
                    );
                }
            } else {
                fastPageStreak = 0;
                if (pageElapsedMs >= 5000 && pageSize > minPageSize) {
                    const previousPageSize = pageSize;
                    pageSize = minPageSize;
                    Logger(
                        `[FastFetchDebug] adaptive slow page; reducing page size ${previousPageSize} -> ${pageSize}`
                    );
                }
            }

            pageSince = page.lastSequence;
            docsToFetch = Math.max(docsToFetch, totalFetched + page.pending);
'''

if old not in s:
    raise SystemExit("adaptive page anchor not found")

p.write_text(s.replace(old, new, 1))
print("Fast Fetch adaptive page sizing applied: start=10 min=5 max=10")

from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    source = path.read_text()
    if old not in source:
        raise SystemExit(f"{label}: anchor not found")
    path.write_text(source.replace(old, new, 1))


streaming = Path("commonlib/src/pouchdb/StreamingFetch.ts")
rebuilder = Path("commonlib/src/serviceModules/Rebuilder.ts")

replace_once(
    streaming,
    '''    const readAvailableChanges = async (pageSince: DBSequence): Promise<number> => {
        const status = await fetchStatus(pageSince);
        if (!Array.isArray(status.results)) {
            throw new StreamingFetchFailure(
                "protocol",
                "Fast Fetch received changes status without a valid results list.",
                false
            );
        }
        const pending = status.pending;
        if (typeof pending !== "number" || !Number.isSafeInteger(pending) || pending < 0) {
            throw new StreamingFetchFailure(
                "protocol",
                "Fast Fetch received changes status without a valid pending count.",
                false
            );
        }
        const available = status.results.length + pending;
        if (!Number.isSafeInteger(available)) {
            throw new StreamingFetchFailure(
                "protocol",
                "Fast Fetch received a changes count outside the supported range.",
                false
            );
        }
        return available;
    };

    const fetchPageNormal = async (pageSince: DBSequence, pageLimit: number): Promise<DBSequence> => {''',
    '''    const fetchPageNormal = async (
        pageSince: DBSequence,
        pageLimit: number
    ): Promise<{ lastSequence: DBSequence; rowCount: number; pending: number }> => {''',
    "direct page function",
)

replace_once(
    streaming,
    '''        if (page.results.length === 0) {
            throw new StreamingFetchFailure(
                "transport",
                "Fast Fetch received no rows after its status probe reported available changes.",
                true
            );
        }

        for (const change of page.results) {''',
    '''        const pending =
            typeof page.pending === "number" && Number.isSafeInteger(page.pending) && page.pending >= 0
                ? page.pending
                : 0;

        if (page.results.length === 0) {
            await batchWriter.flush();
            await saveCheckpoint(onCheckpoint, page.last_seq);
            reportProgress(true);
            return { lastSequence: page.last_seq, rowCount: 0, pending };
        }

        for (const change of page.results) {''',
    "empty page handling",
)

replace_once(
    streaming,
    '''        await batchWriter.flush();
        await saveCheckpoint(onCheckpoint, page.last_seq);
        reportProgress(true);
        return page.last_seq;
    };

    try {
        let pageSince: DBSequence = since;
        let started = false;

        while (true) {
            const available = await readAvailableChanges(pageSince);
            docsToFetch = Math.max(docsToFetch, totalFetched + available);
            if (available === 0) break;

            if (!started) {
                started = true;
                Logger(
                    `Starting initial synchronisation. Current sequence: ${since}, Target sequence: ${progressTargetSeq}, Documents to fetch: ${docsToFetch}.`
                );
            }

            const pageLimit = Math.min(FAST_FETCH_CHANGES_PAGE_LIMIT, available);
            pageSince = await fetchPageNormal(pageSince, pageLimit);
        }
''',
    '''        await batchWriter.flush();
        await saveCheckpoint(onCheckpoint, page.last_seq);
        reportProgress(true);
        return { lastSequence: page.last_seq, rowCount: page.results.length, pending };
    };

    try {
        let pageSince: DBSequence = since;
        let started = false;
        const pageSize = 50;

        while (true) {
            const page = await fetchPageNormal(pageSince, pageSize);
            pageSince = page.lastSequence;
            docsToFetch = Math.max(docsToFetch, totalFetched + page.pending);

            if (page.rowCount > 0 && !started) {
                started = true;
                Logger(
                    `Starting initial synchronisation. Current sequence: ${since}, Target sequence: ${progressTargetSeq}, Documents to fetch: ${docsToFetch}.`
                );
            }

            if (page.rowCount === 0 || page.pending === 0) break;
        }
''',
    "direct page loop",
)

replacements = [
    (
        '    async fetchLocalDBFast(autoResume: boolean) {\n        await this.setting.suspendExtraSync();',
        '    async fetchLocalDBFast(autoResume: boolean) {\n        this._log("[FastFetchDebug] fetchLocalDBFast entered", LOG_LEVEL_NOTICE);\n        await this.setting.suspendExtraSync();',
    ),
    (
        '    private async performFetchLocalDBFast(\n        settings: ReturnType<SettingService["currentSettings"]>,\n        autoResume: boolean\n    ) {\n        this.appLifecycle.resetIsReady();',
        '    private async performFetchLocalDBFast(\n        settings: ReturnType<SettingService["currentSettings"]>,\n        autoResume: boolean\n    ) {\n        this._log("[FastFetchDebug] performFetchLocalDBFast entered", LOG_LEVEL_NOTICE);\n        this.appLifecycle.resetIsReady();',
    ),
    (
        '        } else {\n            await this.resetLocalDatabase();\n            await delay(1000);\n        }\n\n        let localDB = this.database.localDatabase.localDatabase;',
        '        } else {\n            this._log("[FastFetchDebug] Fast Fetch: about to reset local database", LOG_LEVEL_NOTICE);\n            await this.resetLocalDatabase();\n            this._log("[FastFetchDebug] Fast Fetch: resetLocalDatabase returned", LOG_LEVEL_NOTICE);\n            await delay(1000);\n            this._log("[FastFetchDebug] Fast Fetch: post-reset delay finished", LOG_LEVEL_NOTICE);\n        }\n\n        let localDB = this.database.localDatabase.localDatabase;\n        this._log("[FastFetchDebug] Fast Fetch: local DB handle acquired", LOG_LEVEL_NOTICE);',
    ),
    (
        '        const securitySeed = await this.replicator.createRemoteResource(REMOTE_RESOURCE_KINDS.SECURITY_SEED, settings);',
        '        this._log("[FastFetchDebug] Fast Fetch: requesting security seed", LOG_LEVEL_NOTICE);\n        const securitySeed = await this.replicator.createRemoteResource(REMOTE_RESOURCE_KINDS.SECURITY_SEED, settings);\n        this._log("[FastFetchDebug] Fast Fetch: security seed request returned", LOG_LEVEL_NOTICE);',
    ),
    (
        '                    await fetchChangesForInitialSync(\n                        localDB,',
        '                    this._log("[FastFetchDebug] Fast Fetch: about to call fetchChangesForInitialSync", LOG_LEVEL_NOTICE);\n                    await fetchChangesForInitialSync(\n                        localDB,',
    ),
    (
        '    async resetLocalDatabase() {\n        const suffix = this.API.getAppID() || "";',
        '    async resetLocalDatabase() {\n        this._log("[FastFetchDebug] resetLocalDatabase entered", LOG_LEVEL_NOTICE);\n        const suffix = this.API.getAppID() || "";',
    ),
    (
        '        this.events.emitEvent(EVENT_DATABASE_REBUILT);\n    }',
        '        this._log("[FastFetchDebug] resetLocalDatabase: database reset completed; emitting EVENT_DATABASE_REBUILT", LOG_LEVEL_NOTICE);\n        this.events.emitEvent(EVENT_DATABASE_REBUILT);\n        this._log("[FastFetchDebug] resetLocalDatabase: EVENT_DATABASE_REBUILT returned", LOG_LEVEL_NOTICE);\n    }',
    ),
]
for index, (old, new) in enumerate(replacements, 1):
    replace_once(rebuilder, old, new, f"rebuilder diagnostic {index}")

replacements = [
    (
        '    let totalFetched = 0;\n    let totalValidFetched = 0;',
        '    Logger("[FastFetchDebug] fetchChangesForInitialSync entered");\n    let totalFetched = 0;\n    let totalValidFetched = 0;',
    ),
    (
        '        const response = await fetchResponse(\n            statusURL.toString(),',
        '        Logger(`[FastFetchDebug] status probe begin since=${statusSince}`);\n        Logger(`[FastFetchDebug] status probe URL: ${statusURL.toString()}`);\n        const response = await fetchResponse(\n            statusURL.toString(),',
    ),
    (
        '        return parseJSONResponse<DatabaseSyncStatus>(\n            await readResponseText(response, "read changes status"),',
        '        Logger(`[FastFetchDebug] status probe response status: ${response.status}`);\n        const statusRaw = await readResponseText(response, "read changes status");\n        Logger(`[FastFetchDebug] status probe body length: ${statusRaw.length}`);\n        return parseJSONResponse<DatabaseSyncStatus>(\n            statusRaw,',
    ),
    (
        '    const targetStatus = await fetchStatus("now");',
        '    Logger("[FastFetchDebug] target probe starting");\n    const targetStatus = await fetchStatus("now");\n    Logger("[FastFetchDebug] target probe completed");',
    ),
    (
        '        const response = await fetchResponse(\n            changesURL.toString(),',
        '        Logger(`[FastFetchDebug] page fetch starting since=${pageSince} limit=${pageLimit}`);\n        Logger(`[FastFetchDebug] page fetch URL: ${changesURL.toString()}`);\n        const response = await fetchResponse(\n            changesURL.toString(),',
    ),
    (
        '        const raw = await readResponseText(response, "read a bounded normal changes page");',
        '        Logger(`[FastFetchDebug] page fetch response status: ${response.status}`);\n        const raw = await readResponseText(response, "read a bounded normal changes page");\n        Logger(`[FastFetchDebug] page fetch body length: ${raw.length}`);',
    ),
]
for index, (old, new) in enumerate(replacements, 1):
    replace_once(streaming, old, new, f"stream diagnostic {index}")

replace_once(
    streaming,
    '        const page = parseJSONResponse<NormalChangesPage>(raw, "parse a bounded normal changes page");',
    '        Logger("[FastFetchDebug] page JSON parse starting");\n        const page = parseJSONResponse<NormalChangesPage>(raw, "parse a bounded normal changes page");\n        Logger(`[FastFetchDebug] page JSON parse completed rows=${Array.isArray(page.results) ? page.results.length : -1} pending=${page.pending}`);',
    "page parse diagnostics",
)

replace_once(
    streaming,
    '''            totalFetched++;
            if (change.doc) {
                await batchWriter.write(change.doc, change.seq);
                totalValidFetched++;
            } else {''',
    '''            totalFetched++;
            Logger(`[FastFetchDebug] change begin id=${change.id} seq=${String(change.seq)} hasDoc=${Boolean(change.doc)}`);
            if (change.doc) {
                Logger(`[FastFetchDebug] batchWriter.write starting id=${change.id}`);
                await batchWriter.write(change.doc, change.seq);
                Logger(`[FastFetchDebug] batchWriter.write completed id=${change.id}`);
                totalValidFetched++;
            } else {''',
    "change write diagnostics",
)

replace_once(
    streaming,
    '''                try {
                    decryptedDoc = await decryptFunction(doc);
                } catch (error) {''',
    '''                try {
                    Logger(`[FastFetchDebug] decrypt starting id=${doc._id}`);
                    decryptedDoc = await decryptFunction(doc);
                    Logger(`[FastFetchDebug] decrypt completed id=${doc._id}`);
                } catch (error) {''',
    "decrypt diagnostics",
)

replace_once(
    streaming,
    '''            let serialisedDoc: string;
            try {
                const serialised = JSON.stringify(decryptedDoc);''',
    '''            let serialisedDoc: string;
            try {
                Logger(`[FastFetchDebug] serialise starting id=${doc._id}`);
                const serialised = JSON.stringify(decryptedDoc);''',
    "serialise diagnostics start",
)

replace_once(
    streaming,
    '''                serialisedDoc = serialised;
            } catch (error) {''',
    '''                serialisedDoc = serialised;
                Logger(`[FastFetchDebug] serialise completed id=${doc._id} length=${serialisedDoc.length}`);
            } catch (error) {''',
    "serialise diagnostics end",
)

print("Fast Fetch 50-row direct-page patch with deep processing diagnostics applied")

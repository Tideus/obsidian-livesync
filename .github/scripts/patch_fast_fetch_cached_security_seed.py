from pathlib import Path

p = Path("commonlib/src/serviceModules/Rebuilder.ts")
s = p.read_text()

seed_anchor = '''        this._log("[FastFetchDebug] Fast Fetch: security seed request returned", LOG_LEVEL_NOTICE);
        if (!securitySeed) {
            throw new Error("The selected provider cannot supply a Security Seed for Fast Fetch.");
        }
        try {
'''
seed_replacement = '''        this._log("[FastFetchDebug] Fast Fetch: security seed request returned", LOG_LEVEL_NOTICE);
        if (!securitySeed) {
            throw new Error("The selected provider cannot supply a Security Seed for Fast Fetch.");
        }
        try {
            this._log("[FastFetchDebug] Fast Fetch: reading security seed once for cached crypto", LOG_LEVEL_NOTICE);
            const cachedSecuritySeed = await securitySeed.read();
            this._log(
                `[FastFetchDebug] Fast Fetch: cached security seed ready bytes=${cachedSecuritySeed.byteLength}`,
                LOG_LEVEL_NOTICE
            );
'''

callback_anchor = '''                () => securitySeed.read(),
'''
callback_replacement = '''                async () => cachedSecuritySeed,
'''

if seed_anchor not in s:
    raise SystemExit("cached security seed insertion anchor not found")
if callback_anchor not in s:
    raise SystemExit("cached security seed callback anchor not found")

s = s.replace(seed_anchor, seed_replacement, 1)
s = s.replace(callback_anchor, callback_replacement, 1)
p.write_text(s)
print("Fast Fetch cached security seed patch applied")

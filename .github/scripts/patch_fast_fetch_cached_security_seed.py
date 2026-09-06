from pathlib import Path

p = Path("commonlib/src/serviceModules/Rebuilder.ts")
s = p.read_text()

old_seed = '''        const securitySeed = await this.replicator.createRemoteResource(REMOTE_RESOURCE_KINDS.SECURITY_SEED, settings);
        if (!securitySeed) {
            throw new Error("The selected provider cannot supply a Security Seed for Fast Fetch.");
        }
        try {
            const enc = getConfiguredFunctionsForEncryption(
                settings.passphrase,
                false,
                false,
                () => securitySeed.read(),
                settings.E2EEAlgorithm
            );
'''

new_seed = '''        const securitySeed = await this.replicator.createRemoteResource(REMOTE_RESOURCE_KINDS.SECURITY_SEED, settings);
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
            const enc = getConfiguredFunctionsForEncryption(
                settings.passphrase,
                false,
                false,
                async () => cachedSecuritySeed,
                settings.E2EEAlgorithm
            );
'''

if old_seed not in s:
    raise SystemExit("cached security seed anchor not found")

s = s.replace(old_seed, new_seed, 1)
p.write_text(s)
print("Fast Fetch cached security seed patch applied")

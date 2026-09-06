from pathlib import Path

p = Path("commonlib/src/worker/bgWorker.encryption.ts")
s = p.read_text()

old_imports = '''import { startWorker, removeTask } from "./bgWorker.ts";
import { type EncryptHKDFProcessItem, type ResultPayload } from "./universalTypes.ts";
import { type EncryptProcessItem } from "./universalTypes.ts";
import { type EncryptHKDFArguments } from "./universalTypes.ts";
import { type EncryptArguments } from "./universalTypes.ts";
'''
new_imports = '''import { startWorker, removeTask } from "./bgWorker.ts";
import { type EncryptHKDFProcessItem, type ResultPayload } from "./universalTypes.ts";
import { type EncryptProcessItem } from "./universalTypes.ts";
import { type EncryptHKDFArguments } from "./universalTypes.ts";
import { type EncryptArguments } from "./universalTypes.ts";
import { encrypt as directEncrypt, decrypt as directDecrypt } from "octagonal-wheels/encryption";
import { encrypt as directEncryptHKDF, decrypt as directDecryptHKDF } from "octagonal-wheels/encryption/hkdf";

const WORKER_CRYPTO_TIMEOUT_MS = 10000;

async function withWorkerTimeout<T>(promise: Promise<T>, key: number): Promise<T> {
    return await Promise.race([
        promise,
        new Promise<T>((_, reject) => {
            setTimeout(() => reject(new Error(`Background crypto worker timed out after ${WORKER_CRYPTO_TIMEOUT_MS}ms (task ${key})`)), WORKER_CRYPTO_TIMEOUT_MS);
        }),
    ]);
}
'''
if old_imports not in s:
    raise SystemExit("crypto recovery imports anchor not found")
s = s.replace(old_imports, new_imports, 1)

old_v1 = '''export function encryptionOnWorker(data: Omit<EncryptArguments, "key">) {
    const process = startWorker(data);
    return (async () => {
        const ret = await process.task.promise;
        process.finalize();
        return ret;
    })();
}
'''
new_v1 = '''export function encryptionOnWorker(data: Omit<EncryptArguments, "key">) {
    const process = startWorker(data);
    return (async () => {
        try {
            return await withWorkerTimeout(process.task.promise, process.key);
        } catch (ex) {
            const timedOut = ex instanceof Error && ex.message.includes("Background crypto worker timed out");
            if (!timedOut) throw ex;
            console.warn(`[FastFetchDebug] crypto worker timeout task=${process.key} type=${data.type}; using direct fallback`);
            removeTask(process.key);
            if (data.type === "encrypt") {
                return await directEncrypt(data.input, data.passphrase, data.autoCalculateIterations);
            }
            return await directDecrypt(data.input, data.passphrase, data.autoCalculateIterations);
        } finally {
            process.finalize();
        }
    })();
}
'''
if old_v1 not in s:
    raise SystemExit("crypto recovery V1 anchor not found")
s = s.replace(old_v1, new_v1, 1)

old_hkdf = '''export function encryptionHKDFOnWorker(data: Omit<EncryptHKDFArguments, "key">) {
    const process = startWorker(data);
    return (async () => {
        const ret = await process.task.promise;
        process.finalize();
        return ret;
    })();
}
'''
new_hkdf = '''export function encryptionHKDFOnWorker(data: Omit<EncryptHKDFArguments, "key">) {
    const process = startWorker(data);
    return (async () => {
        try {
            return await withWorkerTimeout(process.task.promise, process.key);
        } catch (ex) {
            const timedOut = ex instanceof Error && ex.message.includes("Background crypto worker timed out");
            if (!timedOut) throw ex;
            console.warn(`[FastFetchDebug] crypto worker timeout task=${process.key} type=${data.type}; using direct fallback`);
            removeTask(process.key);
            if (data.type === "encryptHKDF") {
                return await directEncryptHKDF(data.input, data.passphrase, data.pbkdf2Salt);
            }
            return await directDecryptHKDF(data.input, data.passphrase, data.pbkdf2Salt);
        } finally {
            process.finalize();
        }
    })();
}
'''
if old_hkdf not in s:
    raise SystemExit("crypto recovery HKDF anchor not found")
s = s.replace(old_hkdf, new_hkdf, 1)

p.write_text(s)
print("Crypto worker timeout/direct fallback patch applied")

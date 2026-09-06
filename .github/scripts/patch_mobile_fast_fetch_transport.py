from pathlib import Path

p = Path("src/deps.ts")
s = p.read_text()

needle = 'import { type FilePath } from "@vrtmrz/livesync-commonlib/compat/common/types";\n'
insert = '''import { type FilePath } from "@vrtmrz/livesync-commonlib/compat/common/types";\nimport { setFetch } from "@vrtmrz/livesync-commonlib/compat/common/coreEnvFunctions";\nimport { Platform as ObsidianPlatform, requestUrl as obsidianRequestUrl } from "obsidian";\n\nconst browserFetch = globalThis.fetch.bind(globalThis);\n\nif (ObsidianPlatform.isMobileApp) {\n    setFetch(async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {\n        const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;\n        const isFastFetchChanges = url.includes("/_changes?") && url.includes("feed=normal");\n        if (!isFastFetchChanges) {\n            return browserFetch(input, init);\n        }\n\n        const headers: Record<string, string> = {};\n        new Headers(init?.headers).forEach((value, key) => {\n            headers[key] = value;\n        });\n\n        let body: string | ArrayBuffer | undefined;\n        if (typeof init?.body === "string") {\n            body = init.body;\n        } else if (init?.body instanceof ArrayBuffer) {\n            body = init.body;\n        } else if (ArrayBuffer.isView(init?.body)) {\n            const view = init.body;\n            body = view.buffer.slice(view.byteOffset, view.byteOffset + view.byteLength);\n        } else if (init?.body != null) {\n            return browserFetch(input, init);\n        }\n\n        console.log(`[FastFetchDebug] requestUrl transport begin: ${url}`);\n        const nativeResponse = await obsidianRequestUrl({\n            url,\n            method: init?.method ?? "GET",\n            headers,\n            body,\n            throw: false,\n        });\n        console.log(`[FastFetchDebug] requestUrl transport status: ${nativeResponse.status}`);\n\n        const responseHeaders = new Headers();\n        for (const [key, value] of Object.entries(nativeResponse.headers)) {\n            if (typeof value === "string") responseHeaders.set(key, value);\n        }\n\n        return new Response(nativeResponse.arrayBuffer, {\n            status: nativeResponse.status,\n            headers: responseHeaders,\n        });\n    });\n}\n'''

if needle not in s:
    raise SystemExit("deps.ts import anchor not found")

s = s.replace(needle, insert, 1)
p.write_text(s)
print("Mobile requestUrl Fast Fetch transport patch applied")

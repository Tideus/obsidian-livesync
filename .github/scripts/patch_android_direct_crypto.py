from pathlib import Path

p = Path("commonlib/src/pouchdb/encryption.ts")
s = p.read_text()

old = '''import { encryptWorker, decryptWorker, encryptHKDFWorker, decryptHKDFWorker } from "#worker";\n\nexport const encrypt = encryptWorker;\nexport const decrypt = decryptWorker;\nexport const encryptHKDF = encryptHKDFWorker;\nexport const decryptHKDF = decryptHKDFWorker;\n'''
new = '''import { encrypt as directEncrypt, decrypt as directDecrypt } from "octagonal-wheels/encryption";\nimport { encrypt as directEncryptHKDF, decrypt as directDecryptHKDF } from "octagonal-wheels/encryption/hkdf";\n\n// Android 16 diagnostic/recovery build: bypass Web Worker crypto completely.\n// The worker path can stall without firing timers or worker.onerror in Android WebView.\n// Direct crypto keeps the same algorithms and data format, only execution context changes.\nexport const encrypt = directEncrypt;\nexport const decrypt = directDecrypt;\nexport const encryptHKDF = directEncryptHKDF;\nexport const decryptHKDF = directDecryptHKDF;\n'''

if old not in s:
    raise SystemExit("direct crypto anchor not found")

s = s.replace(old, new, 1)
s = s.replace("encryptHKDFWorker(", "directEncryptHKDF(")
s = s.replace("decryptHKDFWorker(", "directDecryptHKDF(")

p.write_text(s)
print("Android direct crypto bypass patch applied")

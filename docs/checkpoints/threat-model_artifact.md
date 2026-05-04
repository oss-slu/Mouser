# Checkpoint Artifact (Choice): **Threat Model** - Mouser

**Project:** Mouser  
**Checkpoint Catalog Item:** Threat Model / Security Risk Assessment   
**Date:** 2026-05-03  

## Artifact identification + rationale

This artifact fulfills the **Threat Model** checkpoint by providing a concrete, system-specific security analysis of Mouser's desktop data-collection workflow. The document identifies assets, trust boundaries, attacker profiles, likely abuse paths, and prioritized mitigations grounded in the current architecture (Tkinter desktop UI, serial/HID device input, SQLite experiment files, and optional `.pmouser` encryption).

We selected this checkpoint now because it is the most meaningful leverage point for the team at this stage: Mouser is expanding operationally, and security weaknesses in local file handling, device input validation, and encrypted file workflows can directly impact experiment integrity, researcher trust, and community adoption. This threat model contributes to the final product by reducing confidentiality/integrity risk and supports the community strategy by giving contributors a shared, actionable security baseline.

---

## Scope and assumptions

**In scope**
- Desktop app runtime (`main.py`, `ui/`, `experiment_pages/`)
- Experiment file lifecycle (`.mouser`, `.pmouser`, temp-copy workflows)
- Local SQLite persistence (`databases/`)
- Serial and HID ingestion paths (`shared/serial_*`, `shared/hid_wedge.py`)
- Local configuration files (`settings/serial ports/...`)

**Out of scope**
- OS/kernel compromise and full-device malware defense
- Network service exposure (Mouser is local-first and not a web service)
- Institutional lab policy compliance controls external to code

**Security objectives**
- Preserve confidentiality of sensitive experiment data
- Preserve integrity of measurements and animal-to-measurement mapping
- Preserve availability during active lab workflows
- Provide auditability and safe failure modes for operators

---

## System context and trust boundaries

### Key assets
- Experiment database content (animals, RFID mappings, measurements, metadata)
- Encrypted experiment files (`.pmouser`) and associated password-derived keys
- Temporary decrypted working copies in OS temp directory
- Serial/HID input streams from lab hardware
- Port configuration files and user-selected hardware preferences

### Trust boundaries
1. **User/Operator boundary**: manual actions in UI, password entry, file selection
2. **Device I/O boundary**: untrusted serial/HID input crossing into parser/UI logic
3. **File boundary**: untrusted external `.mouser/.pmouser` files opened by Mouser
4. **Temp-storage boundary**: decrypted temporary data stored outside app memory
5. **Persistence boundary**: writes from in-memory state to permanent experiment file

---

## Threat actors

- **Accidental operator error**: wrong file, wrong device mapping, unsafe shutdown
- **Curious insider**: local user with filesystem access to temp files/configs
- **Malicious local user/process**: tampers with experiment files or settings
- **Compromised/peripheral device**: emits malformed/noisy/spoofed serial/HID data

---

## STRIDE threat analysis

| ID | STRIDE | Threat scenario | Impact | Current exposure | Priority |
|---|---|---|---|---|---|
| T1 | Spoofing | Rogue HID/serial device injects fake RFID/measurement values | Wrong animal attribution, corrupted data | Input trust is high; limited origin verification | High |
| T2 | Tampering | Local process edits `.mouser` or temp DB during active session | Silent data corruption | Temp DB stored in shared temp path; no integrity check | High |
| T3 | Tampering | Settings files for preferred ports are altered | App binds to attacker-controlled device | Config files are plain text and user-writable | Medium |
| T4 | Repudiation | No durable audit trail of who changed what and when | Investigation/repro difficulty | Minimal logging; no signed action log | Medium |
| T5 | Information Disclosure | Decrypted `.pmouser` temp copy remains recoverable in temp directory | Sensitive data leakage | Decrypted copy written to temp path; cleanup is best-effort | High |
| T6 | Information Disclosure | Static salt for password KDF enables precomputation across files | Reduced resistance to offline attacks | KDF iteration count is strong, but salt is constant | High |
| T7 | Denial of Service | Malformed or high-rate serial input stalls UI or worker loops | Experiment interruption | Threading present, but bounded parsing/rate limiting limited | Medium |
| T8 | Elevation of Privilege | Crafted file payload triggers unsafe parsing or library edge case | App crash/undefined behavior | Mostly SQLite/file operations; no strong schema validation gate | Medium |
| T9 | Tampering/Availability | Save flow writes directly to final file; interruption causes corruption | Data loss | No atomic replace + backup rotation | High |

---

## Risk register and mitigations

### High-priority actions (implement first)

1. **Per-file random salt for `.pmouser` encryption (T6)**
- Generate a random salt per file and store it in a small file header/metadata block.
- Derive key with PBKDF2 using that file-specific salt.
- Keep backward-compatible reader for legacy files with static salt.

2. **Secure temp file strategy for decrypted data (T5, T2)**
- Use uniquely named temp files with restrictive permissions where possible.
- Wipe/delete decrypted temp files on close/save and on startup recovery scan.
- Optionally provide a "memory-only decrypt" mode for sensitive workflows.

3. **Atomic save + rolling backup (T9)**
- Write to `*.tmp`, fsync, then atomic replace target file.
- Keep timestamped backup of previous good file for rollback.

4. **Input validation and framing for RFID/serial payloads (T1, T7)**
- Enforce max length, character class, and expected framing delimiters.
- Reject/control non-conforming payloads with explicit operator feedback.
- Add rate limiting/debouncing to prevent burst overload.

### Medium-priority actions

5. **Settings hardening and validation (T3)**
- Validate config values against allowed enums/ranges.
- Detect and warn on unexpected changes to preferred-port files.

6. **Audit logging for critical actions (T4)**
- Log open/save/export, port changes, and mapping updates with timestamps.
- Store logs in append-only format per experiment session.

7. **File authenticity and integrity checks (T2, T8)**
- Add schema/version validation before open.
- Optionally store checksum/hash metadata for tamper detection warnings.

---

## Abuse-case test checklist (evidence-oriented)

- Attempt open with wrong `.pmouser` password repeatedly and confirm safe failure.
- Simulate abrupt shutdown during save and verify no primary-file corruption.
- Inject oversized/invalid RFID payload and confirm rejection without crash.
- Modify preferred-port config externally; verify warning and safe fallback.
- Validate decrypted temp file cleanup after normal close and crash recovery path.

---

## Contribution to final product and community strategy

This checkpoint strengthens Mouser's final deliverable by protecting the two things that matter most in lab software: **data integrity** and **operator confidence**. The model translates security from a vague requirement into concrete engineering tasks that can be scheduled, reviewed, and tested incrementally.

It also supports community growth by giving contributors a clear security map: where risks live, how to prioritize fixes, and what "done" means for each mitigation. That improves issue quality, reduces review ambiguity, and helps new maintainers make safe changes without needing tribal knowledge.

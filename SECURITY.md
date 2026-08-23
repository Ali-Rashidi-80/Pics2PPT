# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.3.x   | Yes       |
| < 1.3   | No        |

## Reporting a vulnerability

**Pics2PPT is an offline desktop application.** It does not collect telemetry, authenticate users, or make network requests during normal operation.

Persian: [SECURITY.fa.md](SECURITY.fa.md)

If you discover a security issue (e.g., path traversal when processing folder names, unsafe file writes, or dependency CVE with exploitable impact):

1. **Do not** open a public issue for critical vulnerabilities.
2. Email the maintainer: **Ali Rashidi** (via GitHub profile or repository contact once published).
3. Include: version, OS, steps to reproduce, impact assessment.

Expected response: acknowledgment within 7 days.

## Scope notes

| In scope | Out of scope |
|----------|--------------|
| Arbitrary file write outside output folder | PowerPoint macro security (output is macro-free pptx) |
| Malicious image parser crashes (Pillow) | User opening untrusted `.pptx` in PowerPoint |
| PyInstaller bundled DLL issues | Third-party antivirus false positives on unsigned EXE |

## Safe usage

- Run only builds from trusted sources.
- Scan portable EXE with your AV if downloaded from third parties.
- Output `.pptx` files are standard Office Open XML — treat like any office document.

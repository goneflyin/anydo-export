# Any.do One-Time Export

This tool reads a Playwright storage-state export from your own authenticated browser session and converts current Any.do data into JSON files for migration to another system.

## Unofficial Project

This project is unofficial and is not affiliated with, endorsed by, or supported by Any.do.

## Usage Responsibility

Use this tool only for exporting your own data and only if your use complies with Any.do's terms and all applicable laws.

## Why This Exists

This project exists to provide a small, practical, one-time export path for personal data portability when an official export flow is unavailable or insufficient.

## Disclaimer

This code is offered as a convenience and as an example for others.
It is provided without guarantees, and it is not actively maintained.

## Output Files

- `anydo_export.json` — full export from Any.do web IndexedDB (`anydo-sync-db`)
- `anydo_completed_tasks.json` — only tasks with `status == "CHECKED"`
- `anydo_export_summary.json` — counts and quick overview
- `anydo_export_flat.json` — normalized AI-friendly export (`tasks`, `lists`, `labels`, `tags`)

## Security / Redaction

The exporter redacts sensitive auth-like fields in output (keys containing:

- `token`
- `password`
- `auth`
- `idSalt`

Redacted values are replaced with `"[REDACTED]"`.

Redaction is best-effort only. Exported files may still contain sensitive personal or account-related data (for example: task content, notes, participant information, location metadata, and other fields outside current redaction rules). Review output files carefully before sharing them with other people, tools, or AI systems.

## Tested With

- Any.do web at `https://app.any.do` (observed March 2026)
- Playwright `storageState({ indexedDB: true })`
- Python `3.14.3`

## Prerequisite Input

The script expects a Playwright storage-state file at:

- `anydo_storage_state.json`

That file must include IndexedDB for `https://app.any.do`.

## How To Generate `anydo_storage_state.json`

In a Playwright-enabled session (Codex + Playwright MCP):

1. Navigate to `https://app.any.do/`
2. Log in normally (email/password/2FA)
3. Run this in Playwright context:

```js
await page.context().storageState({ path: 'anydo_storage_state.json', indexedDB: true });
```

This writes `anydo_storage_state.json` in the current project directory.

## Run Export

From this directory:

```bash
python3 export_anydo.py
```

## Generate Flat AI-Friendly Export

After `anydo_export.json` exists, run:

```bash
python3 flatten_anydo_export.py
```

This creates `anydo_export_flat.json` with list names resolved on each task and simplified task fields for downstream AI import.

## Example Output (Summary)

Example output from `python3 export_anydo.py`:

```json
{
  "database": "anydo-sync-db",
  "taskCounts": {
    "all": 115,
    "completed": 77,
    "active": 38
  }
}
```

## JSON Shape (Flat Export)

Top-level keys in `anydo_export_flat.json`:

- `exportedAt`
- `source`
- `taskCounts`
- `lists`
- `tags`
- `labels`
- `tasks`

## Known Limitations

- Schema-dependent: Any.do IndexedDB structure may change and break decoding.
- Best-effort redaction: output is not guaranteed safe for public sharing.
- Single-user utility: no multi-account orchestration or long-term maintenance guarantees.

## Optional Cleanup

After successful export, remove the storage-state file to reduce exposure:

```bash
rm -f anydo_storage_state.json
```

## Support

No active support is provided for this project.

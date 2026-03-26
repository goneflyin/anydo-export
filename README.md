# Any.do One-Time Export

This project exports your current Any.do data to JSON files for migration to another system.

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

## Optional Cleanup

After successful export, remove the storage-state file to reduce exposure:

```bash
rm -f anydo_storage_state.json
```

## Support

No active support is provided for this project.

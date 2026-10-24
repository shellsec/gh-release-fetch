# Custom Catalog Implementation Plan

> **For agentic workers:** Implement task by task using the approved design below; use executing-plans for inline execution. Steps use checkbox syntax.

**Goal:** Let users search, add, edit and delete their own application entries from the existing launcher.

**Architecture:** A focused `tools/custom_catalog.py` module owns source parsing, asset inference, preview and persistence. Existing lookup and updater code continue to own searching, download execution and saved lists. `apps-custom/` uses the same platform shard format as other catalogs.

**Tech Stack:** Python 3.10+, standard-library unittest, existing requests/GitHub helpers, PyInstaller.

**Spec (approved in chat):** Custom precedes Search all. Accept a repository name, GitHub repository/Release URL or HTTP(S) package link. Detect platform, architecture and package kind; ambiguous APK/archive platforms require a choice. Preview name/platform/category/package/update mode before confirmation. Offer save only or save and download. Duplicate variants can replace their existing entry. Support editing and deletion. GitHub entries follow release asset rules; ordinary URLs stay fixed.

## Global Constraints

- Reuse existing BAT entry points; no new BAT.
- Keep custom entries separate from curated catalogs and include them in Search all.
- No JSON changes or downloads before the final preview is accepted.
- Do not auto-run imported packages. Do not infer Android TV from a generic APK extension.
- Preserve existing workspace changes; no commits or publishing are part of this request.

## Review Focus

- Cancellation, network/API failure and malformed URLs leave files untouched.
- Version changes retain architecture/variant matching; checksum/source assets are excluded.
- Duplicate names from different owners, or different architectures, do not overwrite each other.
- Update/edit/delete target only the selected custom entry; enabled state survives replacement.
- Frozen EXEs use custom catalogs beside the EXE and correctly route direct-link downloads.

## Tasks

### 1. Model and persistence

Files: `tools/custom_catalog.py`, `tests/test_custom_catalog.py`, `apps-custom/root.json`.

- [x] Write failing tests for source parsing, ambiguous platform inference, stable release matching, duplicate replacement and targeted edit/delete.
- [x] Implement `parse_source`, `detect_assets`, `make_github_entry`, `make_fixed_entry`, `save_entries`, `edit_entry`, `delete_entry`.
- [x] Run `py -3.13 -m unittest discover -s tests -p test_custom_catalog.py -v` until green.

### 2. Interactive flow and updater integration

Files: `lookup_app.py`, `tools/custom_catalog.py`, `auto_update.py`, tests.

- [x] Test preview cancellation, ambiguous selection, save-only, custom search and Search all.
- [x] Add Custom menu / CLI, repository-name search, explicit multi-asset/platform selection and preview confirmation; wire edits/deletion and optional download.
- [x] Add fixed URL resolution and strict filename-pattern matching to the updater; regression-test with future versions and wrong architectures.

### 3. Delivery and verification

Files: readmes, build/package scripts and rebuilt local EXEs.

- [x] Include `apps-custom/` in portable packages and document usage/limitations.
- [x] Run the full focused suite, live API inspection and diff checks.
- [x] Rebuild and exercise root lookup/updater EXEs using a local HTTP fixture and temporary catalogs, without installing packages.

## Execution Notes

The source tree already has pending catalog changes. Keep all of them. Use temporary directories for test imports, edits and deletes.

Approved extension: include a 20-change undo history, actionable attachment/network failure messages, remembered platform/architecture/package preferences, multi-source preview and JSON import/export. Keep private preferences/history out of portable packages; share custom entries explicitly through export.

Verification: 23 focused tests pass, including a real local HTTP download; live GitHub inspection passed for LX desktop, LX TV and VitaShell. Frozen executable flows passed for import, search, edit, delete, undo, export, batch cancellation and preferences. Root lookup_app.exe and auto_update.exe match the verified builds.

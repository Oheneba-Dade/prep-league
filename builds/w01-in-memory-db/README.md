# Builds

## w01-in-memory-db

- **Levels completed:** 2/4 (Levels 1-2 pass; Level 3 has a crash on non-TTL fields; Level 4 not implemented)
- **Minutes used:** 90 minutes

### Reviewer points

1. **Correctness: `get_at` / `delete_at` crash on non-TTL fields.** `set_at` stores `(value, ts)` but both methods read `[2]` unconditionally, so `set_at` then `get_at` raises `IndexError`. This is the most basic Level 3 flow, and the spec's own example hits it.
2. **Design: two storage formats and copy-pasted logic.** `set` stores a bare string, `set_at` stores a tuple, and the scan methods are duplicated four times. Store one shape, `(value, expires_at | None)`, with a single `_is_alive` helper, and have Level 1-2 delegate to the `_at` versions. This is also what Level 4 needs, since backup requires an absolute expiry.
3. **Testing: the tests could not have caught the bug.** They share one module-level DB, so results depend on order, and they skip the cases that matter: `get_at` on a non-TTL field, `set_at` clearing a TTL, `scan_by_prefix_at`, and deleting the last field of a record. Verify each spec table row with a fresh fixture per test.

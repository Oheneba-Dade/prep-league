# Builds

## w01-in-memory-db: strict interviewer review

Review of `w01-in-memory-db/db.py` and `test_db.py`, marked as a strict interviewer.

### Correctness bugs (would fail the interview)

1. **`get_at` and `delete_at` crash on non-TTL fields.** `db.py:56` and `db.py:63` read `[2]` unconditionally. `set_at` stores a 2-tuple, so `set_at("k","g","w",16); get_at("k","g",20)` raises `IndexError`. The spec's own example hits this. The test never calls `get_at` on `g` while it's non-TTL, so it passes.
2. **Level 1 and Level 3 write incompatible formats.** `set` stores a bare string, while `set_at` stores a tuple. Mixing them breaks: `set` then `scan_at` does `len("ann") == 3`, which treats the string as having a TTL. `set_at` then `scan` prints `('v', 5)` as the value. There are two storage schemas in one dict.
3. **Empty records aren't removed.** The spec says "a record with no fields left no longer exists". `delete` and `delete_at` leave `{}` behind, which will make `backup`'s "records with at least one alive field" count wrong unless special-cased.
4. **Expired fields are never evicted.** A record whose fields have all expired stays in the dict as a zombie record.
5. **Level 4 is not implemented.** `backup` and `restore` are `...`. That is a hard fail on the level.

### Design

- **Wrong data model for the next level.** Backup needs "remaining lifetime", which needs an absolute `expires_at`. The code stores `(value, set_ts, ttl)` and recomputes `ts + ttl` in four places. Store `(value, expires_at | None)`, or a small `Field` dataclass, with one `_is_alive(entry, ts)` helper.
- **Levels 1-2 and Level 3 are duplicated.** `scan` and `scan_by_prefix` are copy-pasted into `scan_at` and `scan_by_prefix_at`. Level 1-2 methods should delegate to the `_at` versions (e.g. `ts=0` or `float("inf")`) so there is one code path.
- **`scan_by_prefix_at` should call `scan_at`**, or share a `_scan(key, prefix, ts)` helper.
- **Tuple indexing like `item[1][1] + item[1][2]`** is unreadable. Use unpacking, a dataclass, or a NamedTuple. `len(item[1]) == 3  # has ttl` is a type-tag hack.

### Style and nits

- `self.db[key].pop(field)` followed by `return True` could be `del`.
- `str(item[1])` is defensive noise if you trust the `str` type hints. The test passes `30` as an int and the code silently papers over it. That is a test bug.
- `ret_list` and `item[0]`/`item[1]` should be `result` and `for field, value in sorted(...)`. Prefer f-strings: `f"{field}({value})"`.
- `self.db` is a vague name. `self.records` is better.
- `if key not in self.db: self.db[key] = {}` can be `self.db.setdefault(key, {})`.
- `get` double lookup could be `self.db.get(key, {}).get(field)`.
- `ts` and `ts_to_restore` don't match the spec's `timestamp` and `timestamp_to_restore`. Trivial.

### Tests

- **Module-level shared `db = InMemoryDB()`.** State leaks between tests, so results depend on execution order. Use a fixture. `test_set_level_two` only works because `u1` was already created in test 1.
- **Names are wrong.** `test_set_level_one` also tests get and delete. Name tests by behavior, such as `test_delete_missing_field_returns_false`.
- **Missing assertions from the spec:**
  - `delete("u1","age") == True`, and the record disappearing after its last field is deleted
  - `get` after `delete`
  - `get_at` on a non-TTL field (would have caught bug 1)
  - overwriting a TTL field with `set_at` removing the TTL
  - `scan_by_prefix_at`, which has zero coverage
  - mixed TTL and non-TTL fields in the same scan
  - boundary `ts == expiry - 1`, which is only partly covered
- `== None` and `== False` should be `is None` and `is False`. `import pytest` is unused.
- No Level 4 tests at all.

### What to credit

- The `<=` expiry boundary is right.
- Sorting by field name is right, and the `startswith` prefix is case-sensitive as required.
- The Level 1 and 2 logic is clean and correct.

### Verdict

Levels 1-2 pass. Level 3 passes only on the spec's happy path, with a real `IndexError` on the basic `set_at` then `get_at` flow. Level 4 is absent. The root cause is the dual storage format. Normalizing to `(value, expires_at)` with an `_alive()` helper removes bugs 1-2, collapses the duplication, and makes backup straightforward.

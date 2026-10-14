class InMemoryDB:
    def __init__(self):
        self.db = {}

    # Level 1
    def set(self, key: str, field: str, value: str) -> None:
        if key not in self.db:
            self.db[key] = {}
        self.db[key][field] = value

    def get(self, key: str, field: str) -> str | None:
        if key not in self.db or field not in self.db[key]:
            return None
        return self.db[key][field]

    def delete(self, key: str, field: str) -> bool:
        if key not in self.db or field not in self.db[key]:
            return False
        self.db[key].pop(field)
        return True

    # Level 2
    def scan(self, key: str) -> list[str]:
        if key not in self.db:
            return []
        ret_list = []
        for item in sorted(self.db[key].items()):
            ret_list.append(item[0] + "(" + str(item[1]) + ")")
        return ret_list

    def scan_by_prefix(self, key: str, prefix: str) -> list[str]:
        if key not in self.db:
            return []
        ret_list = []
        for item in sorted(self.db[key].items()):
            if item[0].startswith(prefix):
                ret_list.append(item[0] + "(" + str(item[1]) + ")")
        return ret_list

    # Level 3 (TTL)
    def set_at(self, key: str, field: str, value: str, ts: int) -> None:
        if key not in self.db:
            self.db[key] = {}
        self.db[key][field] = (value, ts)

    def set_at_with_ttl(
        self, key: str, field: str, value: str, ts: int, ttl: int
    ) -> None:
        if key not in self.db:
            self.db[key] = {}
        self.db[key][field] = (value, ts, ttl)

    def get_at(self, key: str, field: str, ts: int) -> str | None:
        if key not in self.db or field not in self.db[key]:
            return None
        if self.db[key][field][1] + self.db[key][field][2] <= ts:
            return None
        return self.db[key][field][0]

    def delete_at(self, key: str, field: str, ts: int) -> bool:
        if key not in self.db or field not in self.db[key]:
            return False
        if self.db[key][field][1] + self.db[key][field][2] <= ts:
            return False
        self.db[key].pop(field)
        return True

    def scan_at(self, key: str, ts: int) -> list[str]:
        if key not in self.db:
            return []
        ret_list = []
        for item in sorted(self.db[key].items()):
            if len(item[1]) == 3:  # has ttl
                if ts < item[1][1] + item[1][2]:
                    ret_list.append(item[0] + "(" + str(item[1][0]) + ")")
            else:
                ret_list.append(item[0] + "(" + str(item[1][0]) + ")")
        return ret_list

    def scan_by_prefix_at(self, key: str, prefix: str, ts: int) -> list[str]:
        if key not in self.db:
            return []
        ret_list = []
        for item in sorted(self.db[key].items()):
            if item[0].startswith(prefix):
                if len(item[1]) == 3:  # has ttl
                    if ts < item[1][1] + item[1][2]:
                        ret_list.append(item[0] + "(" + str(item[1][0]) + ")")
                else:
                    ret_list.append(item[0] + "(" + str(item[1][0]) + ")")
        return ret_list

    # Level 4 (backup)
    def backup(self, ts: int) -> int: ...
    def restore(self, ts: int, ts_to_restore: int) -> None: ...

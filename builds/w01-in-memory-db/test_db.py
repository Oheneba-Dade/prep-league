import pytest
from db import InMemoryDB

db = InMemoryDB()


# Level 1: set, get, delete
def test_set_level_one():
    db.set("u1", "name", "ann")
    assert db.get("u1", "name") == "ann"
    db.set("u1", "name", "bob")
    assert db.get("u1", "name") == "bob"
    assert db.get("u2", "name") == None
    assert db.delete("u1", "zip") == False


def test_set_level_two():
    db.set("u1", "name", "ann")
    db.set("u1", "nickname", "a")
    db.set("u1", "age", 30)
    assert db.scan("u1") == ["age(30)", "name(ann)", "nickname(a)"]
    assert db.scan_by_prefix("u1", "n") == ["name(ann)", "nickname(a)"]
    assert db.scan_by_prefix("u1", "x") == []
    assert db.scan("u9") == []


def test_set_level_three():
    db.set_at_with_ttl("k", "f", "v", 10, 5)
    assert db.get_at("k", "f", 14) == "v"
    assert db.get_at("k", "f", 15) == None
    db.set_at("k", "g", "w", 16)
    assert db.scan_at("k", 20) == ["g(w)"]
    db.set_at_with_ttl("k", "g", "x", 21, 3)
    assert db.get_at("k", "g", 24) == None
    assert db.delete_at("k", "g", 25) == False

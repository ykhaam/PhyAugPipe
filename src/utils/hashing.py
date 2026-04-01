import hashlib


def stable_id(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()

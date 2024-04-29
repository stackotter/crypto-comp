def hashfn(x: bytes) -> int:
    return len(x)


def collide(hash: int) -> bytes:
    return bytes([0] * hash)

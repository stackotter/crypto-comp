def hashfn(x: bytes) -> int:
    return len(x)


def preimage(hash: int) -> bytes:
    return bytes([0] * hash)

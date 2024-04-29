def hashfn(x: bytes) -> int:
    return sum(list(x)) % (2 ** 64)


def preimage(hash: int) -> bytes:
    out = []
    while hash > 255:
        hash -= 255
        out.append(255)
    out.append(hash)
    return out

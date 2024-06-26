HASH_MASK = 2 ** 64 - 1


def rotate_left(x: int, bits: int) -> int:
    return ((x << bits) & HASH_MASK) + (x >> (64 - bits))


def preimage(x: bytes) -> int:
    out = 0
    for b in x:
        out += b
        out &= HASH_MASK
        out = rotate_left(out, 8)
    return out

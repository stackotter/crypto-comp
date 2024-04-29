def hashfn(x: bytes) -> int:
    return len(x)


# Returns plaintext that hashes to the given hash
def preimage(hash: int) -> bytes:
    return bytes([0] * hash)


# Returns new plaintext that hashes to the same hash as the given plaintext
def collide_with(x: bytes) -> bytes:
    if len(x) == 0:
        # No collisions :(
        return None
    collision = list(x)
    collision[0] = 0 if collision[0] == 0 else 1
    return collision


def generate_collisions(n: int) -> [(bytes, bytes)]:
    collisions = []
    for i in range(n):
        x = (i + 1).to_bytes(8)
        collisions.append((x, bytes([0] * 8)))
    return collisions

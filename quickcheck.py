import random
from dataclasses import dataclass


@dataclass
class QuickCheckOpts():
    max_bytes: int
    iters: int


opts = QuickCheckOpts(20, 1000)


def quickcheck_bytes(name: str, fn, predicate) -> float:
    count = opts.iters
    pass_count = 0
    mismatches = []
    crashes = []
    for i in range(count):
        x = random.randbytes(random.randint(0, opts.max_bytes))
        try:
            output = fn(x)
            if predicate(output):
                pass_count += 1
            else:
                mismatches.append((list(x), output))
        except Exception as e:
            print(e)
            crashes.append(list(x))

    print(f"{name}: {pass_count}/{count} cases passed")
    max_mismatches = 5
    for (x, output) in mismatches[:min(max_mismatches, len(mismatches))]:
        print(
            f"  input {x} maps to {output} which doesn't satisfy predicate"
        )
    if len(mismatches) > max_mismatches:
        print(f"  ... ({len(mismatches) - max_mismatches} more failures)")

    max_crashes = 5
    for x in crashes[:min(max_crashes, len(crashes))]:
        print(
            f"  crashes on input {x}"
        )
    if len(crashes) > max_crashes:
        print(f"  ... ({len(crashes) - max_crashes} more crashes)")

    return pass_count / count

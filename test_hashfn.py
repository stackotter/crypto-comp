import importlib
import sys

from quickcheck import quickcheck_bytes, opts as quickcheck_opts

from argparse import ArgumentParser


def test_hash(hashfn):
    quickcheck_bytes(
        "output is uint64", hashfn,
        lambda output: output >= 0 and output < 2 ** 64
    )


def test_preimage(hashfn, preimagefn):
    quickcheck_bytes(
        "preimage collides", lambda x: (
            y := hashfn(x),
            hashfn(preimagefn(y))
        ),
        lambda output: output is not None and output[0] == output[1]
    )


def test_targeted_collision(hashfn, collisionfn):
    # TODO: Support having multiple predicates (just 'and'ing them together
    #   isn't great cause you lose granularity of feedback)
    quickcheck_bytes(
        "collision != input", lambda x: (
            x,
            collisionfn(x)
        ),
        lambda output: output[1] is not None and output[0] != output[1]
    )
    quickcheck_bytes(
        "hash(collision) == hash(input)", lambda x: (
            hashfn(x),
            None if collisionfn(x) is None else hashfn(collisionfn(x))
        ),
        lambda output: output is not None and output[0] == output[1]
    )


def test_arbitrary_collision(hashfn, collisionfn):
    # TODO: Support having multiple predicates (just 'and'ing them together
    #   isn't great cause you lose granularity of feedback)
    collisions_without_duplicates = []
    collisions = collisionfn(quickcheck_opts.iters)
    for collision in collisions:
        if (collision not in collisions_without_duplicates
                and collision is not None
                and (collision[1], collision[0]) not in collisions_without_duplicates):
            collisions_without_duplicates.append(collision)
    collisions = collisions_without_duplicates
    valid_collisions = len(collisions)

    if valid_collisions > quickcheck_opts.iters:
        print(
            f"arbitrary collisions: too many collisions returned ({valid_collisions} > {quickcheck_opts.iters})"
        )
        return

    pass_count = 0
    not_distinct = []
    mismatches = []
    for x, y in collisions:
        if x == y:
            not_distinct.append(x)
        elif (hashed_x := hashfn(x)) != (hashed_y := hashfn(y)):
            mismatches.append((x, y, hashed_x, hashed_y))
        else:
            pass_count += 1
    print(
        f"arbitrary collisions: {pass_count}/{quickcheck_opts.iters} cases passed"
    )
    print(f"  {valid_collisions} valid collisions generated")
    for x in not_distinct:
        print(f"  returned case with both inputs being {x} (not a collision)")
    for (x, y, hashed_x, hashed_y) in mismatches:
        print(f"  case ({x}, {y}) produced {hashed_x} != {hashed_y}")


def import_fn(file: str, fn: str, required: bool = False):
    module_name = "module"
    spec = importlib.util.spec_from_file_location(module_name, file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    try:
        return module.__getattribute__(fn)
    except:
        if required:
            raise f"Missing required function '{fn}'"
        else:
            return None


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--max-bytes", type=int,
                        default=quickcheck_opts.max_bytes)
    parser.add_argument("--iters", type=int,
                        default=quickcheck_opts.iters)
    args = parser.parse_args()

    hash_fn = import_fn(args.file, "hashfn", required=True)
    preimage_fn = import_fn(args.file, "preimage")
    targeted_collision_fn = import_fn(args.file, "collide_with")
    arbitrary_collision_fn = import_fn(
        args.file,
        "generate_collisions"
    )
    quickcheck_opts.max_bytes = args.max_bytes
    quickcheck_opts.iters = args.iters

    test_hash(hash_fn)

    # Functions that generate collisions for provided hashes
    if preimage_fn is not None:
        test_preimage(hash_fn, preimage_fn)

    # Functions that generate collisions for provided plaintexts
    if targeted_collision_fn is not None:
        test_targeted_collision(hash_fn, targeted_collision_fn)

    # Functions that generate lists of arbitrary collisions
    if arbitrary_collision_fn is not None:
        test_arbitrary_collision(hash_fn, arbitrary_collision_fn)

import importlib
import sys

from quickcheck import quickcheck_bytes, opts as quickcheck_opts

from argparse import ArgumentParser


def test_hash(hashfn):
    quickcheck_bytes(
        "output is uint32", hashfn,
        lambda output: output >= 0 and output < 2 ** 32
    )


def test_collision(hashfn, collisionfn):
    quickcheck_bytes(
        "collision collides", lambda x: (
            y := hashfn(x),
            hashfn(collisionfn(y))
        ),
        lambda output: output[0] == output[1]
    )


def import_hashfn(file: str):
    module_name = "hashfn"
    spec = importlib.util.spec_from_file_location(module_name, file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    collisionfn = None
    try:
        collisionfn = module.__getattribute__("collide")
    except:
        pass

    return (
        module.__getattribute__("hashfn"),
        collisionfn
    )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("hashfn_impl_file")
    parser.add_argument("--max-bytes", type=int,
                        default=quickcheck_opts.max_bytes)
    parser.add_argument("--iters", type=int,
                        default=quickcheck_opts.iters)
    args = parser.parse_args()

    (hashfn, collisionfn) = import_hashfn(args.hashfn_impl_file)
    quickcheck_opts.max_bytes = args.max_bytes
    quickcheck_opts.iters = args.iters

    test_hash(hashfn)

    if collisionfn is not None:
        test_collision(hashfn, collisionfn)

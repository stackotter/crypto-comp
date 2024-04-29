import importlib
import sys

from quickcheck import quickcheck_bytes, opts as quickcheck_opts

from argparse import ArgumentParser


def test_hash(hashfn):
    quickcheck_bytes(
        "output is uint32", hashfn,
        lambda output: output >= 0 and output < 2 ** 32
    )


def test_preimage(hashfn, preimagefn):
    quickcheck_bytes(
        "preimage collides", lambda x: (
            y := hashfn(x),
            hashfn(preimagefn(y))
        ),
        lambda output: output[0] == output[1]
    )


def import_hashfn(file: str):
    module_name = "hashfn"
    spec = importlib.util.spec_from_file_location(module_name, file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    preimagefn = None
    try:
        preimagefn = module.__getattribute__("preimage")
    except:
        pass

    return (
        module.__getattribute__("hashfn"),
        preimagefn
    )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("hashfn_impl_file")
    parser.add_argument("--max-bytes", type=int,
                        default=quickcheck_opts.max_bytes)
    parser.add_argument("--iters", type=int,
                        default=quickcheck_opts.iters)
    args = parser.parse_args()

    (hashfn, preimagefn) = import_hashfn(args.hashfn_impl_file)
    quickcheck_opts.max_bytes = args.max_bytes
    quickcheck_opts.iters = args.iters

    test_hash(hashfn)

    if preimagefn is not None:
        test_preimage(hashfn, preimagefn)

#!/user/env python3
# -*- coding: utf-8 -*-

from bjson import dumps, loads
import cProfile
import pstats


def test():
    import time
    import json
    with open("sample.json") as f:
        t = json.load(f)
    t.append("namuyan" * 1024)
    print(t)
    s = time.time()

    pr_dump = cProfile.Profile()
    pr_dump.enable()
    bj = dumps(t)
    pr_dump.disable()
    print("encode", time.time() - s, "Sec")
    stats_dump = pstats.Stats(pr_dump)
    stats_dump.sort_stats('ncalls')
    stats_dump.print_stats()

    pr_load = cProfile.Profile()
    pr_load.enable()
    decoded = loads(bj)
    pr_load.disable()
    print("decode", time.time() - s, "Sec")
    stats_load = pstats.Stats(pr_load)
    stats_load.sort_stats('ncalls')
    stats_load.print_stats()

    print(len(bj) // 1000, "kB, match=", t == decoded)


if __name__ == "__main__":
    test()

# -*- coding: utf-8 -*- #

import oeis


if __name__ == '__main__':
    result = oeis.search('1 2 3 4 5 6')
    print(result.raw.keys())
    first = oeis.Sequence.from_json(result[0])
    print(first.name)
    print(first.meta.keys())

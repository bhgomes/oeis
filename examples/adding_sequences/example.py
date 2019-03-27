# -*- coding: utf-8 -*- #

import oeis


def custom_sequence():
    for i in range(0, 100):
        yield i ** i + i - 1


if __name__ == '__main__':
    entry = oeis.OEIS.register('A9999999', custom_sequence, __module__)
    #for conflict in entry.conflicts:
    #    print(conflict)
    print(entry)

# -*- coding: utf-8 -*- #

import oeis
import numpy as np

sequence = oeis.A(np.random.randint(999999))
print("The {} Sequence!".format(sequence.name))
print(sequence.description)
print(sequence.sample)
print("keywords:", sequence.keywords)
print("author:", sequence.author)
print("metadata:", sequence.meta.keys())

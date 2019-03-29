# oeis
[![Build Status](https://travis-ci.com/bhgomes/oeis.svg?token=yR6xpuQ1eE8snjeofqA8&branch=master)](https://travis-ci.com/bhgomes/oeis)
[![Documentation Status](https://readthedocs.org/projects/oeis/badge/?version=latest)](https://oeis.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/bhgomes/oeis/branch/master/graph/badge.svg?token=vTvXjfMJD9)](https://codecov.io/gh/bhgomes/oeis) 
[![Maintainability](https://api.codeclimate.com/v1/badges/0e5458a2571e7b6c63f6/maintainability)](https://codeclimate.com/github/bhgomes/oeis/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/0e5458a2571e7b6c63f6/test_coverage)](https://codeclimate.com/github/bhgomes/oeis/test_coverage)

_Interface to [OEIS](https://oeis.org)_

## Installation

```bash
pip install oeis-api
```

Go to the [PyPi](https://pypi.org/project/oeis-api) page for more details.

## Documentation

Go to [bhgomes.github.io/oeis](https://bhgomes.github.io/oeis) for documentation.

## Install Anaconda Testing Environment

For quick installation:

```bash
conda create env -f environment.yml
source activate oeis
```

For a more customized environment replace `{ }` with your choices and run:

```bash
conda create -n {environment_name} python={python_version} pip
conda env update -n {environment_name} -f environment.yml
source activate {environment_name}
```

or edit the `environment.yml` file to your choosing.

---

_[Copyright (c) 2019 Brandon Gomes](LICENSE)_

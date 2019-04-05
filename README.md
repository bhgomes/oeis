<div align="center">

# oeis

_Interface to the [OEIS](https://oeis.org)_

[![PyPI](https://img.shields.io/pypi/v/oeis-api.svg)](https://pypi.org/project/oeis-api)
[![Documentation Status](https://readthedocs.org/projects/oeis/badge/?version=latest)](https://oeis.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/bhgomes/oeis.svg?&branch=master)](https://travis-ci.com/bhgomes/oeis)
[![Coverage Status](https://coveralls.io/repos/github/bhgomes/oeis/badge.svg?branch=master)](https://coveralls.io/github/bhgomes/oeis?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/0e5458a2571e7b6c63f6/maintainability)](https://codeclimate.com/github/bhgomes/oeis/maintainability)
[![License](https://img.shields.io/github/license/bhgomes/hexfarm.svg?color=blue)](https://github.com/bhgomes/hexfarm/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

</div>

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

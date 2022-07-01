# Extend MT19937 Predictor

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/NonupleBroken/ExtendMT19937Predictor/Unit%20Testing) ![GitHub](https://img.shields.io/github/license/NonupleBroken/ExtendMT19937Predictor) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/extend-mt19937-predictor) ![PyPI](https://img.shields.io/pypi/v/extend-mt19937-predictor) ![PyPI - Status](https://img.shields.io/pypi/status/extend-mt19937-predictor)

Predict and Backtrack MT19937 PRNG by putting 32 * 624 bits generated numbers.

Python "random" standard library uses mt19937, so we can easily crack it.

## Usage

### Install

```bash
$ pip install extend_mt19937_predictor
```

### Predict

After putting 32 * 624 bits numbers,  the internal state is uniquely determined. And the random number can be predicted at will.

```python
import random
from extend_mt19937_predictor import ExtendMT19937Predictor

predictor = ExtendMT19937Predictor()

for _ in range(624):
    predictor.setrandbits(random.getrandbits(32), 32)

for _ in range(1024):
    assert predictor.predict_getrandbits(32) == random.getrandbits(32)
    assert predictor.predict_getrandbits(64) == random.getrandbits(64)
    assert predictor.predict_getrandbits(128) == random.getrandbits(128)
    assert predictor.predict_getrandbits(256) == random.getrandbits(256)
```

### Backtrack

Besides prediction, it can also backtrack the previous random numbers.

```python
import random
from extend_mt19937_predictor import ExtendMT19937Predictor

numbers = [random.getrandbits(64) for _ in range(1024)]

predictor = ExtendMT19937Predictor()

for _ in range(78):
    predictor.setrandbits(random.getrandbits(256), 256)

_ = [predictor.backtrack_getrandbits(256) for _ in range(78)]

for x in numbers[::-1]:
    assert x == predictor.backtrack_getrandbits(64)
```

### Advanced

`check` param is True by default.  It is ok to put more than 32 * 624 bits numbers when initializing. It will automatically check whether the excess number is the same as the predicted number, and also change the internal state.

 When setting `check` param to False, it will directly overwrite the state without checking.

```python
import random
from extend_mt19937_predictor import ExtendMT19937Predictor

predictor = ExtendMT19937Predictor(check=True)

for _ in range(1024):
    predictor.setrandbits(random.getrandbits(32), 32)

for _ in range(1024):
    assert predictor.predict_getrandbits(32) == random.getrandbits(32)

```

```python
import random
from extend_mt19937_predictor import ExtendMT19937Predictor

predictor = ExtendMT19937Predictor(check=True)

for _ in range(624):
    predictor.setrandbits(random.getrandbits(32), 32)

_ = predictor.setrandbits(0, 32)
# ValueError: this rand number is not correct: 0. should be: 2370104960
```

Besides "random" standard library function `getrandbits`, these functions can be predicted.

```
random
randrange
randint
uniform
```

But only these functions can be backtracked, because of cannot determine how many times the base functions are called by the others.

```
random
uniform
```

## Reference

* https://github.com/kmyk/mersenne-twister-predictor
* https://en.wikipedia.org/wiki/Mersenne_Twister

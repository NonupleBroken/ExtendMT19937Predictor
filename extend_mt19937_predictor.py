import sys
from math import log

N = 624
M = 397
MATRIX_A = 0x9908b0df
UPPER_MASK = 0x80000000
LOWER_MASK = 0x7fffffff


class BaseMT19937Predictor:
    def __init__(self, check=True):
        self._mt = [0] * 624
        self._mti = 0
        self._is_enough = False
        self._check = check

    def setrandbits(self, y, bits):
        if bits % 32:
            raise ValueError("number of bits must be a multiple of 32")
        if not 0 <= y < 2 ** bits:
            raise ValueError("invalid state")
        while bits > 0:
            self._setrand_int32(y & 0xffffffff)
            y >>= 32
            bits -= 32

    def _setrand_int32(self, y):
        """
        Receive the target PRNG's outputs and reconstruct the inner state.
        when 624 consecutive DOWRDs is given, the inner state is uniquely determined.
        """
        assert 0 <= y < 2 ** 32

        if self._is_enough:
            if self._check:
                r = self._predict_getrand_int32()
                if y != r:
                    raise ValueError("this rand number is not correct: %d. should be: %d" % (y, r))
                else:
                    return
            else:
                if self._mti == 0:
                    self._twist()

        self._mt[self._mti] = self._untemper(y)
        self._mti = (self._mti + 1) % N

        if self._mti == 0 and not self._is_enough:
            self._is_enough = True

    def _predict_getrand_int32(self):
        if self._mti == 0:
            self._twist()
        y = self._temper(self._mt[self._mti])
        self._mti = (self._mti + 1) % N
        return y

    def _backtrack_getrand_int32(self):
        self._mti = (self._mti - 1) % N
        y = self._temper(self._mt[self._mti])
        if self._mti == 0:
            self._untwist()
        return y

    def _twist(self):
        for i in range(N):
            y = (self._mt[i] & UPPER_MASK) | (self._mt[(i + 1) % N] & LOWER_MASK)
            self._mt[i] = (y >> 1) ^ self._mt[(i + M) % N]
            if y % 2:
                self._mt[i] ^= MATRIX_A

    def _untwist(self):
        for i in range(N-1, -1, -1):
            t1 = self._mt[i] ^ self._mt[(i + M) % N]
            if (t1 >> 31) & 1:
                t1 ^= MATRIX_A
            high_bit = (t1 >> 30) & 1

            low_bit = 0
            t2 = self._mt[i - 1] ^ self._mt[(i + M - 1) % N]
            if (t2 >> 31) & 1:
                t2 ^= MATRIX_A
                low_bit = 1
            mid_bits = t2 & 0x3fffffff

            y = (high_bit << 31) | (mid_bits << 1) | low_bit
            self._mt[i] = y

    @staticmethod
    def _temper(y):
        y ^= (y >> 11)
        y ^= (y << 7) & 0x9d2c5680
        y ^= (y << 15) & 0xefc60000
        y ^= (y >> 18)
        return y

    @staticmethod
    def _untemper(y):
        y ^= (y >> 18)
        y ^= (y << 15) & 0xefc60000
        y ^= ((y << 7) & 0x9d2c5680) ^ ((y << 14) & 0x94284000) ^ ((y << 21) & 0x14200000) ^ ((y << 28) & 0x10000000)
        y ^= (y >> 11) ^ (y >> 22)
        return y


class ExtendMT19937Predictor(BaseMT19937Predictor):
    def predict_getrandbits(self, bits):
        if bits < 0:
            raise ValueError("number of bits must be greater than zero")
        if not self._is_enough:
            raise ValueError("number of set bits is not enough")
        y = 0
        shift = 0
        while bits > 0:
            t = self._predict_getrand_int32()
            if bits < 32:
                t >>= 32 - bits
            y |= t << shift
            bits -= 32
            shift += 32
        return y

    def backtrack_getrandbits(self, bits):
        if bits < 0:
            raise ValueError("number of bits must be greater than zero")
        if not self._is_enough:
            raise ValueError("number of set bits is not enough")
        y = 0
        while bits > 0:
            t = self._backtrack_getrand_int32()
            shift = 32
            if bits % 32:
                shift = bits % 32
                t >>= 32 - shift
            y |= t << (bits - shift)
            bits -= shift
        return y

    def predict_random(self):
        a = self._predict_getrand_int32() >> 5
        b = self._predict_getrand_int32() >> 6
        return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0)

    def backtrack_random(self):
        b = self._backtrack_getrand_int32() >> 6
        a = self._backtrack_getrand_int32() >> 5
        return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0)

    def _predict_randbelow(self, n):
        """
        Return a random int in the range [0,n).  Returns 0 if n==0.
        """
        if not n:
            return 0
        if sys.version_info[0] == 2:
            k = int(1.00001 + log(n - 1, 2.0))
        else:
            k = n.bit_length()  # don't use (n-1) here because n can be 1
        r = self.predict_getrandbits(k)  # 0 <= r < 2**k
        while r >= n:
            r = self.predict_getrandbits(k)
        return r

    def predict_randrange(self, start, stop=None, step=1):
        """Choose a random item from range(start, stop[, step]).

        This fixes the problem with randint() which includes the
        endpoint; in Python this is usually not what you want.

        """
        if sys.version_info[0] == 2:
            return self._predict_randrange_py2(start, stop, step)
        else:
            return self._predict_randrange_py3(start, stop, step)

    def _predict_randrange_py2(self, start, stop, step):
        BPF = 53
        _maxwidth = 1 << BPF

        istart = int(start)
        if istart != start:
            raise ValueError("non-integer arg 1 for randrange()")
        if stop is None:
            if istart > 0:
                if istart >= _maxwidth:
                    return self._predict_randbelow(istart)
                return int(self.predict_random() * istart)
            raise ValueError("empty range for randrange()")

        # stop argument supplied.
        istop = int(stop)
        if istop != stop:
            raise ValueError("non-integer stop for randrange()")
        width = istop - istart
        if step == 1 and width > 0:
            if width >= _maxwidth:
                return int(istart + self._predict_randbelow(width))
            return int(istart + int(self.predict_random() * width))
        if step == 1:
            raise ValueError("empty range for randrange() (%d,%d, %d)" % (istart, istop, width))

        istep = int(step)
        if istep != step:
            raise ValueError("non-integer step for randrange()")
        if istep > 0:
            n = (width + istep - 1) // istep
        elif istep < 0:
            n = (width + istep + 1) // istep
        else:
            raise ValueError("zero step for randrange()")

        if n <= 0:
            raise ValueError("empty range for randrange()")

        if n >= _maxwidth:
            return istart + istep * self._predict_randbelow(n)
        return istart + istep * int(self.predict_random() * n)

    def _predict_randrange_py3(self, start, stop, step):
        istart = int(start)
        if istart != start:
            raise ValueError("non-integer arg 1 for randrange()")
        if stop is None:
            if istart > 0:
                return self._predict_randbelow(istart)
            raise ValueError("empty range for randrange()")

        istop = int(stop)
        if istop != stop:
            raise ValueError("non-integer stop for randrange()")
        width = istop - istart
        if step == 1 and width > 0:
            return istart + self._predict_randbelow(width)
        if step == 1:
            raise ValueError("empty range for randrange() (%d, %d, %d)" % (istart, istop, width))

        istep = int(step)
        if istep != step:
            raise ValueError("non-integer step for randrange()")
        if istep > 0:
            n = (width + istep - 1) // istep
        elif istep < 0:
            n = (width + istep + 1) // istep
        else:
            raise ValueError("zero step for randrange()")

        if n <= 0:
            raise ValueError("empty range for randrange()")

        return istart + istep * self._predict_randbelow(n)

    def predict_randint(self, a, b):
        """
        Return random integer in range [a, b], including both end points.
        """
        return self.predict_randrange(a, b+1)

    def predict_uniform(self, a, b):
        """
        Get a random number in the range [a, b) or [a, b] depending on rounding.
        """
        return a + (b - a) * self.predict_random()

    def backtrack_uniform(self, a, b):
        return a + (b - a) * self.backtrack_random()

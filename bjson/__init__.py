from bjson.bjson_ver2 import _dumps_ver2, _loads_ver2
from bjson.body import Data
from bjson.exception import *
from io import BytesIO
import zlib


__version__ = '0.2.10'
__lowest_protocol__ = 2
__highest_protocol__ = 2
ORDER = 'big'
LOWEST_PROTOCOL = int(__lowest_protocol__).to_bytes(1, ORDER)
HIGHEST_PROTOCOL = int(__highest_protocol__).to_bytes(1, ORDER)


def dumps(obj, compress=False):
    try:
        b = BytesIO()
        _dumps_ver2(obj=obj, b=b)
        r = b.getvalue()
        b.close()
    except Exception as e:
        raise BJsonEncodeError(e)

    if compress:
        return b'\x00' + HIGHEST_PROTOCOL + zlib.compress(r)
    else:
        return b'\x01' + HIGHEST_PROTOCOL + r


def dump(obj, fp, compress=False):
    assert 'b' in fp.mode, 'Need binary mode'
    fp.write(dumps(obj=obj, compress=compress))


def loads(b, check_ver=True):
    f_compressed = (b[0] == 0)
    version = b[1]
    if __lowest_protocol__ <= version <= __highest_protocol__:
        pass
    else:
        raise BJsonVersionError("Failed check version. [{}<={}<={}]"
                                .format(__lowest_protocol__, version, __highest_protocol__))

    b = zlib.decompress(b[2:]) if f_compressed else b[2:]

    try:
        i = Data()
        i.all = len(b)
        if version == 2:
            result = _loads_ver2(b=b, i=i)
        else:
            raise BJsonVersionError('Why?')
    except Exception as e:
        raise BJsonDecodeError(e)

    if i.all == i.index:
        return result
    else:
        raise BJsonDecodeError('output binary isn\'t zero. %s' % b)


def load(fp, check_ver=True):
    assert 'b' in fp.mode, 'Need binary mode'
    b = fp.read()
    return loads(b=b, check_ver=check_ver)


__all__ = [
    "dumps",
    "dump",
    "loads",
    "load"
]

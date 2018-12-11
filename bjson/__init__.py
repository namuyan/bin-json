from bjson.ver2 import _dumps_ver2, _loads_ver2
from bjson.ver3 import *
from bjson.body import Data
from bjson.exception import *
from threading import Lock
from io import BytesIO
import zlib


__version__ = '0.2.12'
__lowest_protocol__ = 2
__highest_protocol__ = 3
ORDER = 'big'
LOWEST_PROTOCOL = int(__lowest_protocol__).to_bytes(1, ORDER)
HIGHEST_PROTOCOL = int(__highest_protocol__).to_bytes(1, ORDER)
RECOMMEND_PROTOCOL = LOWEST_PROTOCOL
lock = Lock()


def dumps(obj, compress=False, proto=None):
    if proto is None:
        proto = RECOMMEND_PROTOCOL
    else:
        proto = proto.to_bytes(1, 'big')
    try:
        if proto == LOWEST_PROTOCOL:
            b = BytesIO()
            _dumps_ver2(obj=obj, b=b)
            r = b.getvalue()
            b.close()
        elif proto == HIGHEST_PROTOCOL:
            with lock:
                bio = init_dump_ver3()
                _dumps_ver3(obj=obj)
                r = bio.getvalue()
                bio.close()
        else:
            raise BJsonVersionError('Why?')
    except Exception as e:
        raise BJsonEncodeError(e)

    if compress:
        return b'\x00' + proto + zlib.compress(r)
    else:
        return b'\x01' + proto + r


def dump(obj, fp, compress=False, proto=HIGHEST_PROTOCOL):
    assert 'b' in fp.mode, 'Need binary mode'
    fp.write(dumps(obj=obj, compress=compress, proto=proto))


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
        if version == 2:
            i = Data()
            i.all = len(b)
            result = _loads_ver2(b=b, i=i)
        elif version == 3:
            with lock:
                i = init_load_ver3(byte=b)
                result = _loads_ver3()
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

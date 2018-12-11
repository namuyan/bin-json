from bjson.body import Data
from bjson.exception import *
import struct
from io import BytesIO
"""
protocol version 3
"""

ORDER = 'big'
BOOL = 0
INT = 1
MINUS_INT = 2
COMPLEX = 3
FLOAT = 4
STR = 5
BYTES = 6
LIST = 7
TUPLE = 8
SET = 9
DICT = 10
NULL = 11
BIN_BOOL = BOOL.to_bytes(1, byteorder=ORDER)
BIN_INT = INT.to_bytes(1, byteorder=ORDER)
BIN_MINUS_INT = MINUS_INT.to_bytes(1, byteorder=ORDER)
BIN_COMPLEX = COMPLEX.to_bytes(1, byteorder=ORDER)
BIN_FLOAT = FLOAT.to_bytes(1, byteorder=ORDER)
BIN_STR = STR.to_bytes(1, byteorder=ORDER)
BIN_BYTES = BYTES.to_bytes(1, byteorder=ORDER)
BIN_LIST = LIST.to_bytes(1, byteorder=ORDER)
BIN_TUPLE = TUPLE.to_bytes(1, byteorder=ORDER)
BIN_SET = SET.to_bytes(1, byteorder=ORDER)
BIN_DICT = DICT.to_bytes(1, byteorder=ORDER)
BIN_NULL = NULL.to_bytes(1, byteorder=ORDER)


def init_dump_ver3():
    global bio
    bio = BytesIO()
    return bio


def init_load_ver3(byte: bytes):
    global b, d
    b = byte
    d = Data()
    d.all = len(b)
    return d


def int2bin(obj):
    if obj <= 0xfb:
        bio.write(obj.to_bytes(1, ORDER))
    elif obj <= 0xffff:
        bio.write(b'\xfc')
        bio.write(obj.to_bytes(2, ORDER))
    elif obj <= 0xffffffffffffffff:
        bio.write(b'\xfd')
        bio.write(obj.to_bytes(8, ORDER))
    elif obj <= 0xffffffffffffffffffffffffffffffff:
        bio.write(b'\xfe')
        bio.write(obj.to_bytes(16, ORDER))
    elif obj <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff:
        bio.write(b'\xff')
        bio.write(obj.to_bytes(32, ORDER))
    else:
        raise BJsonEncodeError('Int too big to encode!')


def _dumps_ver3(obj: object):
    if isinstance(obj, bool):
        bio.write(BIN_BOOL)
        bio.write(b'\x01' if obj else b'\x00')

    elif isinstance(obj, int) and 0 <= obj:
        bio.write(BIN_INT)
        int2bin(obj)

    elif isinstance(obj, int):
        bio.write(BIN_MINUS_INT)
        int2bin(obj * -1)

    elif isinstance(obj, complex):
        bio.write(BIN_COMPLEX)
        real = struct.pack("d", obj.real)
        imag = struct.pack("d", obj.imag)
        bio.write(real + imag)

    elif isinstance(obj, float):
        bio.write(BIN_FLOAT)
        bio.write(struct.pack("d", obj))

    elif isinstance(obj, str):
        bio.write(BIN_STR)
        str_bytes = obj.encode()
        int2bin(len(str_bytes))
        bio.write(str_bytes)

    elif isinstance(obj, bytes):
        bio.write(BIN_BYTES)
        int2bin(len(obj))
        bio.write(obj)

    elif isinstance(obj, list):
        bio.write(BIN_LIST)
        int2bin(len(obj))
        for o in obj:
            _dumps_ver3(o)

    elif isinstance(obj, tuple):
        bio.write(BIN_TUPLE)
        int2bin(len(obj))
        for o in obj:
            _dumps_ver3(o)

    elif isinstance(obj, set):
        bio.write(BIN_SET)
        int2bin(len(obj))
        for o in sorted(obj):
            _dumps_ver3(o)

    elif isinstance(obj, dict):
        bio.write(BIN_DICT)
        int2bin(len(obj))
        sorted_list = sorted(obj)
        for k in sorted_list:
            _dumps_ver3(k)
        for k in sorted_list:
            _dumps_ver3(obj[k])

    elif isinstance(obj, type(None)):
        bio.write(BIN_NULL)
    else:
        raise BJsonEncodeError('Unknown type %s' % type(obj))


def bin2int():
    first = b[d.index]
    d.index += 1
    if first <= 0xfb:
        result = first
    elif first == 0xfc:
        result = int.from_bytes(b[d.index:d.index + 2], ORDER)
        d.index += 2
    elif first == 0xfd:
        result = int.from_bytes(b[d.index:d.index + 8], ORDER)
        d.index += 8
    elif first == 0xfe:
        result = int.from_bytes(b[d.index:d.index + 16], ORDER)
        d.index += 16
    else:
        # first == 0xff
        result = int.from_bytes(b[d.index:d.index + 32], ORDER)
        d.index += 32
    return result


def _loads_ver3():
    b_type = b[d.index]
    d.index += 1

    if b_type == BOOL:
        result = True if b[d.index] == 1 else False
        d.index += 1

    elif b_type == INT:
        result = bin2int()

    elif b_type == MINUS_INT:
        result = bin2int()
        result *= -1

    elif b_type == COMPLEX:
        real = struct.unpack("d", b[d.index:d.index + 8])[0]
        d.index += 8
        imag = struct.unpack("d", b[d.index:d.index + 8])[0]
        d.index += 8
        result = complex(real, imag)

    elif b_type == FLOAT:
        result = struct.unpack("d", b[d.index:d.index + 8])[0]
        d.index += 8

    elif b_type == STR:
        bin_len = bin2int()
        result = b[d.index:d.index + bin_len].decode()
        d.index += bin_len

    elif b_type == BYTES:
        bin_len = bin2int()
        result = b[d.index:d.index + bin_len]
        d.index += bin_len

    elif b_type == LIST:
        list_len = bin2int()
        result = [_loads_ver3() for dummy in range(list_len)]

    elif b_type == TUPLE:
        tuple_len = bin2int()
        result = tuple(_loads_ver3() for dummy in range(tuple_len))

    elif b_type == SET:
        set_len = bin2int()
        result = {_loads_ver3() for dummy in range(set_len)}

    elif b_type == DICT:
        dict_len = bin2int()
        key = [_loads_ver3() for dummy in range(dict_len)]
        value = [_loads_ver3() for dummy in range(dict_len)]
        result = {key[i]: value[i] for i in range(dict_len)}

    elif b_type == NULL:
        result = None

    else:
        raise BJsonDecodeError('Unknown type %d' % b_type)
    return result


__all__ = [
    "init_dump_ver3",
    "init_load_ver3",
    "_dumps_ver3",
    "_loads_ver3",
]
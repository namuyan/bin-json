from bjson.body import Data
from bjson.exception import *
import math
import struct
from io import BytesIO

"""
protocol version 2
"""

ORDER = 'big'
BOOL = 0
INT = 1
MINUS_INT = 2
COMPLEX = 3
FLOAT = 4
STR = 5
STR_LONG = 6
BYTES = 7
LIST = 8
TUPLE = 9
SET = 10
DICT = 11
NULL = 12
BIN_BOOL = BOOL.to_bytes(1, byteorder=ORDER)
BIN_INT = INT.to_bytes(1, byteorder=ORDER)
BIN_MINUS_INT = MINUS_INT.to_bytes(1, byteorder=ORDER)
BIN_COMPLEX = COMPLEX.to_bytes(1, byteorder=ORDER)
BIN_FLOAT = FLOAT.to_bytes(1, byteorder=ORDER)
BIN_STR = STR.to_bytes(1, byteorder=ORDER)
BIN_STR_LONG = STR_LONG.to_bytes(1, byteorder=ORDER)
BIN_BYTES = BYTES.to_bytes(1, byteorder=ORDER)
BIN_LIST = LIST.to_bytes(1, byteorder=ORDER)
BIN_TUPLE = TUPLE.to_bytes(1, byteorder=ORDER)
BIN_SET = SET.to_bytes(1, byteorder=ORDER)
BIN_DICT = DICT.to_bytes(1, byteorder=ORDER)
BIN_NULL = NULL.to_bytes(1, byteorder=ORDER)


def _dumps_ver2(obj, b: BytesIO):
    if isinstance(obj, bool):
        b.write(BIN_BOOL)
        b.write(b'\x01' if obj else b'\x00')

    elif isinstance(obj, int) and obj >= 0:
        b.write(BIN_INT)
        int_pow = 1 if obj == 0 else max(1, int(math.log(obj, 256) + 1))
        b.write(int_pow.to_bytes(1, byteorder=ORDER))
        b.write(obj.to_bytes(int_pow, byteorder=ORDER))

    elif isinstance(obj, int):
        b.write(BIN_MINUS_INT)
        i = -1 * obj
        int_pow = 1 if i == 0 else max(1, int(math.log(i, 256) + 1))
        b.write(int_pow.to_bytes(1, byteorder=ORDER))
        b.write(i.to_bytes(int_pow, byteorder=ORDER))

    elif isinstance(obj, complex):
        b.write(BIN_COMPLEX)
        real = struct.pack("d", obj.real)
        imag = struct.pack("d", obj.imag)
        b.write(real + imag)

    elif isinstance(obj, float):
        b.write(BIN_FLOAT)
        b.write(struct.pack("d", obj))

    elif isinstance(obj, str) and len(obj) < 256:
        b.write(BIN_STR)
        str_bytes = obj.encode()
        b.write(len(str_bytes).to_bytes(1, byteorder=ORDER))
        b.write(str_bytes)

    elif isinstance(obj, str):
        b.write(BIN_STR_LONG)
        str_bytes = obj.encode()
        str_len = len(str_bytes)
        str_pow = 1 if str_len == 0 else max(1, int(math.log(str_len, 256) + 1))
        b.write(str_pow.to_bytes(1, byteorder=ORDER))
        b.write(str_len.to_bytes(str_pow, byteorder=ORDER))
        b.write(str_bytes)

    elif isinstance(obj, bytes):
        b.write(BIN_BYTES)
        byte_len = len(obj)
        byte_pow = 1 if byte_len == 0 else max(1, int(math.log(byte_len, 256) + 1))
        b.write(byte_pow.to_bytes(1, byteorder=ORDER))
        b.write(byte_len.to_bytes(byte_pow, byteorder=ORDER))
        b.write(obj)

    elif isinstance(obj, list):
        b.write(BIN_LIST)
        i = len(obj)
        int_pow = 1 if i == 0 else max(1, int(math.log(i, 256) + 1))
        b.write(int_pow.to_bytes(1, byteorder=ORDER))
        b.write(i.to_bytes(int_pow, byteorder=ORDER))
        for n in obj:
            _dumps_ver2(obj=n, b=b)

    elif isinstance(obj, tuple):
        b.write(BIN_TUPLE)
        i = len(obj)
        int_pow = 1 if i == 0 else max(1, int(math.log(i, 256) + 1))
        b.write(int_pow.to_bytes(1, byteorder=ORDER))
        b.write(i.to_bytes(int_pow, byteorder=ORDER))
        for n in obj:
            _dumps_ver2(obj=n, b=b)

    elif isinstance(obj, set):
        b.write(BIN_SET)
        i = len(obj)
        int_pow = 1 if i == 0 else max(1, int(math.log(i, 256) + 1))
        b.write(int_pow.to_bytes(1, byteorder=ORDER))
        b.write(i.to_bytes(int_pow, byteorder=ORDER))
        for n in sorted(obj):
            _dumps_ver2(obj=n, b=b)

    elif isinstance(obj, dict):
        b.write(BIN_DICT)
        i = len(obj)
        int_pow = 1 if i == 0 else max(1, int(math.log(i, 256) + 1))
        b.write(int_pow.to_bytes(1, byteorder=ORDER))
        b.write(i.to_bytes(int_pow, byteorder=ORDER))
        for k in sorted(obj):
            _dumps_ver2(obj=k, b=b)
            _dumps_ver2(obj=obj[k], b=b)

    elif isinstance(obj, type(None)):
        b.write(BIN_NULL)
    else:
        raise BJsonEncodeError('Unknown type %s' % type(obj))


def _loads_ver2(b: bytes, i: Data):
    b_type = b[i.index]
    i.index += 1

    if b_type == BOOL:
        result = True if b[i.index] == 1 else False
        i.index += 1
    elif b_type == INT:
        bin_pow = b[i.index]
        result = int.from_bytes(b[i.index + 1:i.index + 1 + bin_pow], byteorder=ORDER)
        i.index += 1 + bin_pow
    elif b_type == MINUS_INT:
        bin_pow = b[i.index]
        result = int.from_bytes(b[i.index + 1:i.index + 1 + bin_pow], byteorder=ORDER) * -1
        i.index += 1 + bin_pow
    elif b_type == COMPLEX:
        real = struct.unpack("d", b[i.index:i.index + 8])[0]
        i.index += 8
        imag = struct.unpack("d", b[i.index:i.index + 8])[0]
        i.index += 8
        result = complex(real, imag)
    elif b_type == FLOAT:
        result = struct.unpack("d", b[i.index:i.index+8])[0]
        i.index += 8
    elif b_type == STR:
        bin_len = b[i.index]
        result = b[i.index + 1:i.index + 1 + bin_len].decode()
        i.index += 1 + bin_len
    elif b_type == STR_LONG:
        bin_pow = b[i.index]
        bin_len = int.from_bytes(b[i.index + 1:i.index + 1 + bin_pow], byteorder=ORDER)
        result = b[i.index + 1 + bin_pow:i.index + 1 + bin_pow + bin_len].decode()
        i.index += 1 + bin_pow + bin_len
    elif b_type == BYTES:
        bin_pow = b[i.index]
        bin_len = int.from_bytes(b[i.index + 1:i.index + 1 + bin_pow], byteorder=ORDER)
        result = b[i.index + 1 + bin_pow:i.index + 1 + bin_pow + bin_len]
        i.index += 1 + bin_pow + bin_len

    elif b_type == LIST:
        bin_pow = b[i.index]
        list_len = int.from_bytes(b[i.index + 1:i.index + 1 + bin_pow], byteorder=ORDER)
        i.index += 1 + bin_pow
        result = [_loads_ver2(b=b, i=i) for dummy in range(list_len)]

    elif b_type == TUPLE:
        bin_pow = b[i.index]
        tuple_len = int.from_bytes(b[i.index + 1:i.index + 1 + bin_pow], byteorder=ORDER)
        i.index += 1 + bin_pow
        result = tuple(_loads_ver2(b=b, i=i) for dummy in range(tuple_len))

    elif b_type == SET:
        bin_pow = b[i.index]
        set_len = int.from_bytes(b[i.index + 1:i.index + 1 + bin_pow], byteorder=ORDER)
        i.index += 1 + bin_pow
        result = {_loads_ver2(b=b, i=i) for dummy in range(set_len)}

    elif b_type == DICT:
        bin_pow = b[i.index]
        dict_len = int.from_bytes(b[i.index + 1:i.index + 1 + bin_pow], byteorder=ORDER)
        i.index += 1 + bin_pow
        result = dict()
        for dummy in range(dict_len):
            k = _loads_ver2(b=b, i=i)
            v = _loads_ver2(b=b, i=i)
            result[k] = v

    elif b_type == NULL:
        result = None

    else:
        raise BJsonDecodeError('Unknown type %d' % b_type)
    return result

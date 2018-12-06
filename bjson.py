#!/user/env python3
# -*- coding: utf-8 -*-

import math
import struct
import zlib
from io import BytesIO

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
VERSION = int(2).to_bytes(1, byteorder=ORDER)
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


class Index:
    index = 0
    all = 0


def _dumps(obj, b):
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
            _dumps(obj=n, b=b)

    elif isinstance(obj, tuple):
        b.write(BIN_TUPLE)
        i = len(obj)
        int_pow = 1 if i == 0 else max(1, int(math.log(i, 256) + 1))
        b.write(int_pow.to_bytes(1, byteorder=ORDER))
        b.write(i.to_bytes(int_pow, byteorder=ORDER))
        for n in obj:
            _dumps(obj=n, b=b)

    elif isinstance(obj, set):
        b.write(BIN_SET)
        i = len(obj)
        int_pow = 1 if i == 0 else max(1, int(math.log(i, 256) + 1))
        b.write(int_pow.to_bytes(1, byteorder=ORDER))
        b.write(i.to_bytes(int_pow, byteorder=ORDER))
        for n in sorted(obj):
            _dumps(obj=n, b=b)

    elif isinstance(obj, dict):
        b.write(BIN_DICT)
        i = len(obj)
        int_pow = 1 if i == 0 else max(1, int(math.log(i, 256) + 1))
        b.write(int_pow.to_bytes(1, byteorder=ORDER))
        b.write(i.to_bytes(int_pow, byteorder=ORDER))
        for k in sorted(obj):
            _dumps(obj=k, b=b)
            _dumps(obj=obj[k], b=b)

    elif isinstance(obj, type(None)):
        b.write(BIN_NULL)
    else:
        raise BJsonEncodeError('Unknown type %s' % type(obj))


def dumps(obj, compress=False):
    try:
        b = BytesIO()
        _dumps(obj=obj, b=b)
        r = b.getvalue()
        b.close()
    except Exception as e:
        raise BJsonEncodeError(e)

    if compress:
        return b'\x00' + VERSION + zlib.compress(r)
    else:
        return b'\x01' + VERSION + r


def dump(obj, fp, compress=False):
    assert 'b' in fp.mode, 'Need binary mode'
    fp.write(dumps(obj=obj, compress=compress))


def _loads(b, i):
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
        result = [_loads(b=b, i=i) for dummy in range(list_len)]

    elif b_type == TUPLE:
        bin_pow = b[i.index]
        tuple_len = int.from_bytes(b[i.index + 1:i.index + 1 + bin_pow], byteorder=ORDER)
        i.index += 1 + bin_pow
        result = tuple(_loads(b=b, i=i) for dummy in range(tuple_len))

    elif b_type == SET:
        bin_pow = b[i.index]
        set_len = int.from_bytes(b[i.index + 1:i.index + 1 + bin_pow], byteorder=ORDER)
        i.index += 1 + bin_pow
        result = {_loads(b=b, i=i) for dummy in range(set_len)}

    elif b_type == DICT:
        bin_pow = b[i.index]
        dict_len = int.from_bytes(b[i.index + 1:i.index + 1 + bin_pow], byteorder=ORDER)
        i.index += 1 + bin_pow
        result = dict()
        for dummy in range(dict_len):
            k = _loads(b=b, i=i)
            v = _loads(b=b, i=i)
            result[k] = v

    elif b_type == NULL:
        result = None

    else:
        raise BJsonDecodeError('Unknown type %d' % b_type)
    return result


def loads(b, check_ver=True):
    f_compressed = (b[0] == 0)
    i_version = b[1].to_bytes(1, byteorder=ORDER)
    if check_ver and i_version != VERSION:
        raise BJsonVersionError("Do not match bjson version. this:{}, input:{}"
                                .format(VERSION[0], i_version[0]))

    b = zlib.decompress(b[2:]) if f_compressed else b[2:]
    i = Index()
    i.all = len(b)
    try:
        result = _loads(b=b, i=i)
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


class BJsonBaseError(Exception): pass


class BJsonEncodeError(BJsonBaseError): pass


class BJsonDecodeError(BJsonBaseError): pass


class BJsonVersionError(BJsonBaseError): pass

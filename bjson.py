#!/user/env python3
# -*- coding: utf-8 -*-

import math
import struct
import zlib

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


class BinaryTool:
    @staticmethod
    def float2bin(f):
        return struct.pack("d", f)

    @staticmethod
    def bin2float(b, i):
        r = struct.unpack("d", b[i.index:i.index + 8])[0]
        i.index += 8
        return r

    @staticmethod
    def str2bin(s):
        str_bytes = s.encode()
        str_len = len(str_bytes)
        return str_len.to_bytes(1, byteorder=ORDER) + str_bytes

    @staticmethod
    def bin2str(b, i):
        bin_len = b[i.index]
        r = b[i.index + 1:i.index + 1 + bin_len].decode()
        i.index += 1 + bin_len
        return r

    @staticmethod
    def str_long2bin(s):
        str_bytes = s.encode()
        str_len = len(str_bytes)
        str_pow = 1 if str_len == 0 else max(1, int(math.log(str_len, 256) + 1))
        return str_pow.to_bytes(1, byteorder=ORDER) + str_len.to_bytes(str_pow, byteorder=ORDER) + str_bytes

    @staticmethod
    def bin2str_long(b, i):
        bin_pow = b[i.index]
        bin_len = int.from_bytes(b[i.index + 1:i.index + 1 + bin_pow], byteorder=ORDER)
        bin_str = b[i.index + 1 + bin_pow:i.index + 1 + bin_pow + bin_len].decode()
        i.index += 1 + bin_pow + bin_len
        return bin_str

    @staticmethod
    def int2bin(i):
        int_pow = 1 if i == 0 else max(1, int(math.log(i, 256) + 1))
        return int_pow.to_bytes(1, byteorder=ORDER) + i.to_bytes(int_pow, byteorder=ORDER)

    @staticmethod
    def bin2int(b, i):
        bin_pow = b[i.index]
        bin_int = int.from_bytes(b[i.index + 1:i.index + 1 + bin_pow], byteorder=ORDER)
        i.index += 1 + bin_pow
        return bin_int

    @staticmethod
    def byte2bin(h):
        byte_len = len(h)
        byte_pow = 1 if byte_len == 0 else max(1, int(math.log(byte_len, 256) + 1))
        return byte_pow.to_bytes(1, byteorder=ORDER) + byte_len.to_bytes(byte_pow, byteorder=ORDER) + h

    @staticmethod
    def bin2byte(b, i):
        bin_pow = b[i.index]
        bin_len = int.from_bytes(b[i.index + 1:i.index + 1 + bin_pow], byteorder=ORDER)
        bin_byte = b[i.index + 1 + bin_pow:i.index + 1 + bin_pow + bin_len]
        i.index += 1 + bin_pow + bin_len
        return bin_byte

    @staticmethod
    def bool2bin(tf):
        return b'\x01' if tf else b'\x00'

    @staticmethod
    def bin2bool(b, i):
        r = True if b[i.index] == 1 else False
        i.index += 1
        return r

    @staticmethod
    def cmp2bin(c):
        real = BinaryTool.float2bin(f=c.real)
        imag = BinaryTool.float2bin(f=c.imag)
        return real + imag

    @staticmethod
    def bin2cmp(b, i):
        real = BinaryTool.bin2float(b=b, i=i)
        imag = BinaryTool.bin2float(b=b, i=i)
        return complex(real=real, imag=imag)


def _dumps(obj):
    if isinstance(obj, bool):
        b = BIN_BOOL
        b += BinaryTool.bool2bin(tf=obj)
    elif isinstance(obj, int) and obj >= 0:
        b = BIN_INT
        b += BinaryTool.int2bin(i=obj)

    elif isinstance(obj, int):
        b = BIN_MINUS_INT
        b += BinaryTool.int2bin(i=-1 * obj)

    elif isinstance(obj, complex):
        b = BIN_COMPLEX
        b += BinaryTool.cmp2bin(c=obj)

    elif isinstance(obj, float):
        b = BIN_FLOAT
        b += BinaryTool.float2bin(f=obj)

    elif isinstance(obj, str) and len(obj) < 256:
        b = BIN_STR
        b += BinaryTool.str2bin(s=obj)

    elif isinstance(obj, str):
        b = BIN_STR_LONG
        b += BinaryTool.str_long2bin(s=obj)

    elif isinstance(obj, bytes):
        b = BIN_BYTES
        b += BinaryTool.byte2bin(h=obj)

    elif isinstance(obj, list):
        b = BIN_LIST
        b += BinaryTool.int2bin(i=len(obj))
        for n in obj:
            b += _dumps(obj=n)

    elif isinstance(obj, tuple):
        b = BIN_TUPLE
        b += BinaryTool.int2bin(i=len(obj))
        for n in obj:
            b += _dumps(obj=n)

    elif isinstance(obj, set):
        b = BIN_SET
        b += BinaryTool.int2bin(i=len(obj))
        for n in sorted(obj):
            b += _dumps(obj=n)

    elif isinstance(obj, dict):
        b = BIN_DICT
        b += BinaryTool.int2bin(i=len(obj))
        for k in sorted(obj):
            b += _dumps(obj=k)
            b += _dumps(obj=obj[k])

    elif isinstance(obj, type(None)):
        b = BIN_NULL
    else:
        raise BJsonEncodeError('Unknown type %s' % type(obj))
    return b


def dumps(obj, compress=True):
    try:
        b = _dumps(obj=obj)
    except Exception as e:
        raise BJsonEncodeError(e)

    if compress:
        return b'\x00' + VERSION + zlib.compress(b)
    else:
        return b'\x01' + VERSION + b


def dump(obj, fp, compress=True):
    assert 'b' in fp.mode, 'Need binary mode'
    fp.write(dumps(obj=obj, compress=compress))


def _loads(b, i):
    b_type = b[i.index]
    i.index += 1

    if b_type == BOOL:
        result = BinaryTool.bin2bool(b=b, i=i)
    elif b_type == INT:
        result = BinaryTool.bin2int(b=b, i=i)
    elif b_type == MINUS_INT:
        result = BinaryTool.bin2int(b=b, i=i) * -1
    elif b_type == COMPLEX:
        result = BinaryTool.bin2cmp(b=b, i=i)
    elif b_type == FLOAT:
        result = BinaryTool.bin2float(b=b, i=i)
    elif b_type == STR:
        result = BinaryTool.bin2str(b=b, i=i)
    elif b_type == STR_LONG:
        result = BinaryTool.bin2str_long(b=b, i=i)
    elif b_type == BYTES:
        result = BinaryTool.bin2byte(b=b, i=i)

    elif b_type == LIST:
        list_len = BinaryTool.bin2int(b=b, i=i)
        result = [_loads(b=b, i=i) for dummy in range(list_len)]

    elif b_type == TUPLE:
        tuple_len = BinaryTool.bin2int(b=b, i=i)
        result = tuple(_loads(b=b, i=i) for dummy in range(tuple_len))

    elif b_type == SET:
        set_len = BinaryTool.bin2int(b=b, i=i)
        result = {_loads(b=b, i=i) for dummy in range(set_len)}

    elif b_type == DICT:
        dict_len = BinaryTool.bin2int(b=b, i=i)
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
        raise BJsonVersionError("Do not match bjson version. this:%s, input:%s" % (VERSION, i_version))

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

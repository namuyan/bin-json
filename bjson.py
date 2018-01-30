#!/user/env python3
# -*- coding: utf-8 -*-

import math
import struct
import zlib

ORDER = 'big'
INT = 0
FLOAT = 1
STR = 2
STR_LONG = 3
BYTES = 4
LIST = 5
TUPLE = 6
SET = 7
DICT = 8
VERSION = int(1).to_bytes(1, byteorder=ORDER)
BIN_INT = INT.to_bytes(1, byteorder=ORDER)
BIN_FLOAT = FLOAT.to_bytes(1, byteorder=ORDER)
BIN_STR = STR.to_bytes(1, byteorder=ORDER)
BIN_STR_LONG = STR_LONG.to_bytes(1, byteorder=ORDER)
BIN_BYTES = BYTES.to_bytes(1, byteorder=ORDER)
BIN_LIST = LIST.to_bytes(1, byteorder=ORDER)
BIN_TUPLE = TUPLE.to_bytes(1, byteorder=ORDER)
BIN_SET = SET.to_bytes(1, byteorder=ORDER)
BIN_DICT = DICT.to_bytes(1, byteorder=ORDER)


class BinaryTool:
    @staticmethod
    def float2bin(f):
        return struct.pack("d", f)

    @staticmethod
    def bin2float(b):
        return struct.unpack("d", b[:8])[0], b[8:]

    @staticmethod
    def str2bin(s):
        str_len = len(s.encode())
        return str_len.to_bytes(1, byteorder=ORDER) + s.encode()

    @staticmethod
    def bin2str(b):
        bin_len = b[0]
        return b[1:1+bin_len].decode(), b[1+bin_len:]

    @staticmethod
    def str_long2bin(s):
        str_len = len(s.encode())
        str_pow = 1 if str_len == 0 else max(1, int(math.log(str_len, 256) + 1))
        return str_pow.to_bytes(1, byteorder=ORDER) + str_len.to_bytes(str_pow, byteorder=ORDER) + s.encode()

    @staticmethod
    def bin2str_long(b):
        bin_pow = b[0]
        bin_len = int.from_bytes(b[1:1+bin_pow], byteorder=ORDER)
        bin_str = b[1+bin_pow:1+bin_pow+bin_len].decode()
        return bin_str, b[1+bin_pow+bin_len:]

    @staticmethod
    def str2bin_test(s):
        byte_str = s.encode()
        if len(byte_str) < 256:
            return b'\x00' + len(byte_str).to_bytes(1, byteorder=ORDER) + byte_str
        elif len(byte_str) < 18446744073709551616:
            return b'\x01' + len(byte_str).to_bytes(8, byteorder=ORDER) + byte_str
        else:
            raise Exception("string is too long!")

    @staticmethod
    def bin2str_test(b):
        if b[0] == 0:
            str_len = b[1]
            return b[2:2 + str_len].decode(), b[2 + str_len:]
        else:
            str_len = int.from_bytes(b[1:9], byteorder=ORDER)
            return b[9:9 + str_len].decode(), b[9 + str_len:]

    @staticmethod
    def int2bin(i):
        int_pow = 1 if i == 0 else max(1, int(math.log(i, 256) + 1))
        return int_pow.to_bytes(1, byteorder=ORDER) + i.to_bytes(int_pow, byteorder=ORDER)

    @staticmethod
    def bin2int(b):
        bin_pow = b[0]
        bin_int = int.from_bytes(b[1:1+bin_pow], byteorder=ORDER)
        return bin_int, b[1+bin_pow:]

    @staticmethod
    def byte2bin(h):
        byte_len = len(h)
        byte_pow = 1 if byte_len == 0 else max(1, int(math.log(byte_len, 256) + 1))
        return byte_pow.to_bytes(1, byteorder=ORDER) + byte_len.to_bytes(byte_pow, byteorder=ORDER) + h

    @staticmethod
    def bin2byte(b):
        bin_pow = b[0]
        bin_len = int.from_bytes(b[1:1+bin_pow], byteorder=ORDER)
        bin_byte = b[1+bin_pow:1+bin_pow+bin_len]
        return bin_byte, b[1+bin_pow+bin_len:]


def _dumps(obj):
    t = type(obj)
    if t == int:
        b = BIN_INT
        b += BinaryTool.int2bin(i=obj)

    elif t == float:
        b = BIN_FLOAT
        b += BinaryTool.float2bin(f=obj)

    elif t == str and len(obj) < 256:
        b = BIN_STR
        b += BinaryTool.str2bin(s=obj)

    elif t == str:
        b = BIN_STR_LONG
        b += BinaryTool.str_long2bin(s=obj)

    elif t == bytes:
        b = BIN_BYTES
        b += BinaryTool.byte2bin(h=obj)

    elif t == list:
        b = BIN_LIST
        b += BinaryTool.int2bin(i=len(obj))
        for n in obj:
            b += _dumps(obj=n)

    elif t == tuple:
        b = BIN_TUPLE
        b += BinaryTool.int2bin(i=len(obj))
        for n in obj:
            b += _dumps(obj=n)

    elif t == set:
        b = BIN_SET
        b += BinaryTool.int2bin(i=len(obj))
        for n in sorted(obj):
            b += _dumps(obj=n)

    elif t == dict:
        b = BIN_DICT
        b += BinaryTool.int2bin(i=len(obj))
        for k in sorted(obj):
            b += _dumps(obj=k)
            b += _dumps(obj=obj[k])
    else:
        raise BJsonEncodeError('Unknown type %s' % type(obj))
    return b


def dumps(obj, compress=True):
    b = _dumps(obj=obj)
    if compress:
        return b'\x00' + VERSION + zlib.compress(b)
    else:
        return b'\x01' + VERSION + b


def dump(obj, fp, compress=True):
    assert 'b' in fp.mode, 'Need binary mode'
    fp.write(dumps(obj=obj, compress=compress))


def _loads(b):
    b_type, b = b[0], b[1:]

    if b_type == INT:
        result, b = BinaryTool.bin2int(b=b)
    elif b_type == FLOAT:
        result, b = BinaryTool.bin2float(b=b)
    elif b_type == STR:
        result, b = BinaryTool.bin2str(b=b)
    elif b_type == STR_LONG:
        result, b = BinaryTool.bin2str_long(b=b)
    elif b_type == BYTES:
        result, b = BinaryTool.bin2byte(b=b)

    elif b_type == LIST:
        list_len, b = BinaryTool.bin2int(b=b)
        result = list()
        for dummy in range(list_len):
            element, b = _loads(b=b)
            result.append(element)

    elif b_type == TUPLE:
        tuple_len, b = BinaryTool.bin2int(b=b)
        result = list()
        for dummy in range(tuple_len):
            element, b = _loads(b=b)
            result.append(element)
        else:
            result = tuple(result)

    elif b_type == SET:
        set_len, b = BinaryTool.bin2int(b=b)
        result = set()
        for dummy in range(set_len):
            element, b = _loads(b=b)
            result.add(element)

    elif b_type == DICT:
        dict_len, b = BinaryTool.bin2int(b=b)
        result = dict()
        for dummy in range(dict_len):
            k, b = _loads(b=b)
            v, b = _loads(b=b)
            result[k] = v
    else:
        raise BJsonDecodeError('Unknown type %d' % b_type)
    return result, b


def loads(b, check_ver=True):
    f_compressed = b[0] == 0
    i_version = b[1].to_bytes(1, byteorder=ORDER)
    if check_ver and i_version != VERSION:
        raise BJsonVersionError("Do not match bjson version. this:%d, input:%d" % (VERSION, i_version))

    b = zlib.decompress(b[2:]) if f_compressed else b[2:]
    result, b = _loads(b=b)
    if len(b) == 0:
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

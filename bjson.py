#!/user/env python3
# -*- coding: utf-8 -*-

import math
import struct

ORDER = 'big'
INT = 0
FLOAT = 1
STR = 2
BYTES = 3
LIST = 4
TUPLE = 5
SET = 6
DICT = 7
BIN_INT = INT.to_bytes(1, byteorder=ORDER)
BIN_FLOAT = FLOAT.to_bytes(1, byteorder=ORDER)
BIN_STR = STR.to_bytes(1, byteorder=ORDER)
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
        str_pow = 1 if str_len == 0 else max(1, int(math.log(str_len, 256) + 1))
        return str_pow.to_bytes(1, byteorder=ORDER) + str_len.to_bytes(str_pow, byteorder=ORDER) + s.encode()

    @staticmethod
    def bin2str(b):
        bin_pow = b[0]
        bin_len = int.from_bytes(b[1:1+bin_pow], byteorder=ORDER)
        bin_str = b[1+bin_pow:1+bin_pow+bin_len].decode()
        return bin_str, b[1+bin_pow+bin_len:]

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


def dumps(obj):
    t = type(obj)
    if t == int:
        b = BIN_INT
        b += BinaryTool.int2bin(i=obj)

    elif t == float:
        b = BIN_FLOAT
        b += BinaryTool.float2bin(f=obj)

    elif t == str:
        b = BIN_STR
        b += BinaryTool.str2bin(s=obj)

    elif t == bytes:
        b = BIN_BYTES
        b += BinaryTool.byte2bin(h=obj)

    elif t == list:
        b = BIN_LIST
        b += BinaryTool.int2bin(i=len(obj))
        for n in obj:
            b += dumps(obj=n)

    elif t == tuple:
        b = BIN_TUPLE
        b += BinaryTool.int2bin(i=len(obj))
        for n in obj:
            b += dumps(obj=n)

    elif t == set:
        b = BIN_SET
        b += BinaryTool.int2bin(i=len(obj))
        for n in sorted(obj):
            b += dumps(obj=n)

    elif t == dict:
        b = BIN_DICT
        b += BinaryTool.int2bin(i=len(obj))
        for k in sorted(obj):
            b += dumps(obj=k)
            b += dumps(obj=obj[k])
    else:
        raise EnvironmentError('Unknown type %s' % type(obj))
    return b


def _loads(b):
    b_type, b = b[0], b[1:]

    if b_type == INT:
        result, b = BinaryTool.bin2int(b=b)
    elif b_type == FLOAT:
        result, b = BinaryTool.bin2float(b=b)
    elif b_type == STR:
        result, b = BinaryTool.bin2str(b=b)
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
        raise EnvironmentError('Unknown type %d' % b_type)
    return result, b


def loads(b):
    result, b = _loads(b=b)
    if len(b) == 0:
        return result
    else:
        raise EnvironmentError('bjson decode error')


def test():
    import time
    import json
    with open("sample.json") as f:
        t = json.load(f)
    print(t)
    s = time.time()
    bj = dumps(t)
    print("encode", time.time() - s)
    print(bj)
    print(t == loads(bj))
    print("decode", time.time() - s)

if __name__ == "__main__":
    test()

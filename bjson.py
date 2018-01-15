#!/user/env python3
# -*- coding: utf-8 -*-

import math

INT = 0
STR = 1
BYTES = 2
LIST = 3
TUPLE = 4
SET = 5
DICT = 6
BIN_INT = INT.to_bytes(1, 'big')
BIN_STR = STR.to_bytes(1, 'big')
BIN_BYTES = BYTES.to_bytes(1, 'big')
BIN_LIST = LIST.to_bytes(1, 'big')
BIN_TUPLE = TUPLE.to_bytes(1, 'big')
BIN_SET = SET.to_bytes(1, 'big')
BIN_DICT = DICT.to_bytes(1, 'big')


class BinaryTool:
    @staticmethod
    def str2bin(s):
        str_len = len(s.encode())
        str_pow = 1 if str_len == 0 else max(1, int(math.log(str_len, 256) + 1))
        return str_pow.to_bytes(1, 'big') + str_len.to_bytes(str_pow, 'big') + s.encode()

    @staticmethod
    def bin2str(b):
        bin_pow, b = int.from_bytes(b[:1], 'big'), b[1:]
        bin_len, b = int.from_bytes(b[:bin_pow], 'big'), b[bin_pow:]
        bin_str, b = b[:bin_len], b[bin_len:]
        return bin_str.decode(), b

    @staticmethod
    def int2bin(i):
        int_pow = 1 if i == 0 else max(1, int(math.log(i, 256) + 1))
        return int_pow.to_bytes(1, 'big') + i.to_bytes(int_pow, 'big')

    @staticmethod
    def bin2int(b):
        bin_pow, b = int.from_bytes(b[:1], 'big'), b[1:]
        bin_int, b = int.from_bytes(b[:bin_pow], 'big'), b[bin_pow:]
        return bin_int, b

    @staticmethod
    def byte2bin(h):
        byte_len = len(h)
        byte_pow = 1 if byte_len == 0 else max(1, int(math.log(byte_len, 256) + 1))
        return byte_pow.to_bytes(1, 'big') + byte_len.to_bytes(byte_pow, 'big') + h

    @staticmethod
    def bin2byte(b):
        bin_pow, b = int.from_bytes(b[:1], 'big'), b[1:]
        bin_len, b = int.from_bytes(b[:bin_pow], 'big'), b[bin_pow:]
        bin_byte, b = b[:bin_len], b[bin_len:]
        return bin_byte, b


def dumps(obj):
    t = type(obj)
    b = b''
    if t == int:
        b = BIN_INT
        b += BinaryTool.int2bin(i=obj)

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
    b_type, b = int.from_bytes(b[:1], 'big'), b[1:]

    if b_type == INT:
        result, b = BinaryTool.bin2int(b=b)
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
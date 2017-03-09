#!/usr/bin/python3
# -*- coding: utf-8 -*-

import string


def get_binary_code(c: str):
    if c in string.ascii_uppercase:
        return bin(ord(c) - ord('A'))[2:].zfill(6)
    elif c in string.ascii_lowercase:
        return bin(ord(c) - ord('a') + 26)[2:].zfill(6)
    elif c in string.digits:
        return bin(ord(c) - ord('0') + 26 * 2)[2:].zfill(6)
    elif c == '+':
        return '111110'
    elif c == '/':
        return '111111'
    elif c == '=':
        return ''
    else:
        raise ValueError("Uexpected char: {}".format(c))


def decode_from_base64(source: str):
    pre_data = ''.join(get_binary_code(c) for c in source)
    return bytes((int(pre_data[index * 8:index * 8 + 8], 2)) for index in range(len(pre_data) // 8))


def main():
    data = decode_from_base64('U2ltcGxlIGV4YW1wbGU=')
    print(data)

if __name__ == '__main__':
    main()
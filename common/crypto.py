# -*- coding: utf-8 -*-
# @Time: 2024/1/1
# @Author: Administrator
# @File: crypto.py
import hashlib
from json import loads, dumps
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import struct


def md5(data: str):
    return hashlib.md5(data.encode('utf8')).hexdigest()


def pack(data: bytes):
    return struct.pack('I', len(data))


def unpack(data: bytes):
    return struct.unpack('I', data)[0]


def generate_key_and_iv():
    key = get_random_bytes(16)  # 128-bit 密钥
    iv = get_random_bytes(16)  # 128-bit IV
    return key, iv


KEY, IV = generate_key_and_iv()
BLOCK_SIZE = 1024 * 1024


def encrypt_data(file, data: dict):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    with open(file, 'wb') as f:
        f.write(KEY)
        f.write(IV)
        encrypted_chunk = cipher.encrypt(pad(str(data).encode('utf8'), AES.block_size))
        f.write(encrypted_chunk)


def decrypt_data(file):
    with open(file, 'rb') as f:
        key = f.read(16)
        iv = f.read(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypt = unpad(cipher.decrypt(f.read()), AES.block_size)
        return eval(decrypt)


def encrypt_file(encrypted_file, save_file):
    with open(encrypted_file, 'rb') as f_input, open(save_file, 'wb') as f_output:
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        f_output.write(KEY)
        f_output.write(IV)
        data_chunk = f_input.read(BLOCK_SIZE)
        encrypted_chunk = cipher.encrypt(pad(data_chunk, AES.block_size))
        pack_data = pack(encrypted_chunk)
        f_output.write(pack_data)
        f_output.write(encrypted_chunk)
        while True:
            data = f_input.read(BLOCK_SIZE)
            if data:
                f_output.write(data)
            else:
                break


def decrypt_file(decrypted_file, save_file):
    with open(decrypted_file, 'rb') as f_input, open(save_file, 'wb') as f_output:
        key = f_input.read(16)
        iv = f_input.read(16)
        length_data = f_input.read(4)
        length = unpack(length_data)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        data_chunk = f_input.read(length)
        decrypted_chunk = unpad(cipher.decrypt(data_chunk), AES.block_size)
        f_output.write(decrypted_chunk)
        while True:
            data = f_input.read(BLOCK_SIZE)
            if data:
                f_output.write(data)
            else:
                break


def file_md5(file_path: str) -> str:
    md5 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            block = f.read(BLOCK_SIZE)
            if not block:
                break
            md5.update(block)
    return md5.hexdigest()


def main():
    input_file = r'F:\求生之路2\2509195428.vpk'
    encrypted_file = r'F:\求生之路2\2509195428.bin'
    decrypted_file = r'F:\求生之路2\2509195428.bin.vpk'
    # assert file_md5(input_file) == file_md5(decrypted_file)
    encrypt_file(input_file, encrypted_file)
    decrypt_file(encrypted_file, decrypted_file)


if __name__ == '__main__':
    print(md5('2824268260'))
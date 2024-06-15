# -*- coding: utf-8 -*-
# @Time    : 2018/11/2 11:38
# @Author  : Will
# @Email   : 864311352@qq.com
# @File    : encryption.py
# @Software: PyCharm

import base64

from Crypto.Cipher import AES  # str不是16的倍数那就补足为16的倍数

from config import default_config


class Encryption(object):
    def __init__(self):
        self.key = default_config.SECRET_KEY
        self.aes = AES.new(self.pad_key(self.key), AES.MODE_ECB)

    def encrypt(self, text):
        """
        Encrypt the given text using AES encryption.

        :param text: The plaintext to encrypt.
        :return: The encrypted text in base64 format.
        """
        padded_text = self.pad_text(text)
        encrypted_bytes = self.aes.encrypt(padded_text)
        encrypted_text = base64.b64encode(encrypted_bytes).decode('utf-8')
        return encrypted_text

    def decrypt(self, encrypted_text):
        """
        Decrypt the given encrypted text using AES encryption.

        :param encrypted_text: The encrypted text in base64 format.
        :return: The decrypted plaintext.
        """
        encrypted_bytes = base64.b64decode(encrypted_text)
        decrypted_bytes = self.aes.decrypt(encrypted_bytes)
        decrypted_text = decrypted_bytes.rstrip(b'\0').decode('utf-8')
        return decrypted_text

    def pad_key(self, key):
        """
        Pad the key to make its length a multiple of 16.

        :param key: The original key.
        :return: The padded key.
        """
        return self.pad_text(key)

    def pad_text(self, text):
        """
        Pad the text to make its length a multiple of 16.

        :param text: The original text.
        :return: The padded text.
        """
        while len(text) % 16 != 0:
            text += '\0'
        return text.encode('utf-8')


if __name__ == '__main__':
    value = Encryption().decrypt("yLGS2SgqldmtI1PoD05jjQ==")
    print(value)

    value = Encryption().encrypt("uGWDy24p7f1vLVMK")
    print(value)

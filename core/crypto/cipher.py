from Crypto.Cipher import AES


class AESCipher(object):
    iv = b'\x02\xf8\x14Rn\xc3\xfd\x87\xc2B\x1c(M\xc6\x11\xa2'

    def encrypt(self, message, key):
        message = self._pad(message, 32)

        cipher = AES.new(key, AES.MODE_CBC, self.iv)
        return cipher.encrypt(message)

    def decrypt(self, data, key):
        cipher = AES.new(key, AES.MODE_CBC, self.iv)
        return cipher.decrypt(data)

    @staticmethod
    def _pad(message, bytes_count):
        return message + (bytes_count - len(message) % bytes_count) * b'0'

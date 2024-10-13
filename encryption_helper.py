class EncryptionHelper:
    def __init__(self, key=65):  # Predefined encryption key (65)
        self.key = key

    def xor_encrypt(self, message):
        return ''.join([chr(ord(c) ^ self.key) for c in message])

    def xor_decrypt(self, message):
        return ''.join([chr(ord(c) ^ self.key) for c in message])

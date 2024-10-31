import binascii

class EncryptionHelper:
    def __init__(self, key='KEY'):
        self.key = key.upper()  # Ensure the key is uppercase
        self.key_length = len(self.key)

    def encrypt(self, plaintext):
        encrypted_text = []
        for i, char in enumerate(plaintext):
            if char.isalpha():  # Only encrypt alphabetic characters
                shift = ord(self.key[i % self.key_length]) - 65  # A = 0, B = 1, ..., Z = 25
                if char.isupper():
                    encrypted_char = chr((ord(char) - 65 + shift) % 26 + 65)  # Encrypt uppercase
                else:
                    encrypted_char = chr((ord(char) - 97 + shift) % 26 + 97)  # Encrypt lowercase
                encrypted_text.append(encrypted_char)
            else:
                encrypted_text.append(char)  # Non-alphabetic characters remain unchanged
        return ''.join(encrypted_text)

    def decrypt(self, ciphertext):
        decrypted_text = []
        for i, char in enumerate(ciphertext):
            if char.isalpha():  # Only decrypt alphabetic characters
                shift = ord(self.key[i % self.key_length]) - 65  # A = 0, B = 1, ..., Z = 25
                if char.isupper():
                    decrypted_char = chr((ord(char) - 65 - shift) % 26 + 65)  # Decrypt uppercase
                else:
                    decrypted_char = chr((ord(char) - 97 - shift) % 26 + 97)  # Decrypt lowercase
                decrypted_text.append(decrypted_char)
            else:
                decrypted_text.append(char)  # Non-alphabetic characters remain unchanged
        return ''.join(decrypted_text)

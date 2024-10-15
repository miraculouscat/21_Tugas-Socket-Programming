class EncryptionHelper:
    def __init__(self, shift=3):
        self.shift = shift

    def encrypt(self, text):
        return ''.join([chr(((ord(char) - 65 + self.shift) % 26) + 65) if char.isupper() 
                        else chr(((ord(char) - 97 + self.shift) % 26) + 97) if char.islower()
                        else char for char in text])

    def decrypt(self, text):
        return ''.join([chr(((ord(char) - 65 - self.shift) % 26) + 65) if char.isupper() 
                        else chr(((ord(char) - 97 - self.shift) % 26) + 97) if char.islower()
                        else char for char in text])

from crypto.base import CryptoCode


class CaesarCode (CryptoCode):
    def __init__(self, offset=3):
        self.offset = offset

    def encrypt(self):
        char_list = []
        for i in range(len(self.plain_text)):
            v = ord(self.plain_text[i]) + self.offset
            if v > ord('z'):
                v -= 26
            char_list.append(v)
        self.encrypt_text = bytearray(char_list)

    def decrypt(self):
        char_list = []
        for i in range(len(self.encrypt_text)):
            v = self.encrypt_text[i] - self.offset
            if v < ord('a'):
                v += 26

            char_list.append(v)
        self.result_txt = bytearray(char_list)


if __name__ == '__main__':
    c = CaesarCode()
    c.main()
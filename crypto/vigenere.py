from crypto.base import CryptoCode


class Vigenere(CryptoCode):
    def __init__(self, key="helloworld"):
        self.key = key

    def encrypt(self):
        char_list = []
        for i in range(len(self.plain_text)):
            v = ord(self.plain_text[i]) + ord(self.key[i % len(self.key)]) - ord('a')
            if v > ord('z'):
                v -= 26
            char_list.append(v)
        self.encrypt_text = bytearray(char_list)

    def decrypt(self):
        char_list = []
        for i in range(len(self.encrypt_text)):
            v = self.encrypt_text[i] - ord(self.key[i % len(self.key)]) + ord('a')
            if v < ord('a'):
                v += 26

            char_list.append(v)
        self.result_txt = bytearray(char_list)

    def print_repetition(self):
        repetition_dict = []
        for sub_length in range(4,8):
            for i in range(len(self.encrypt_text)-sub_length+1):
                for j in range(i+sub_length, len(self.encrypt_text)-sub_length+1):
                    if self.encrypt_text[i:i+sub_length] == self.encrypt_text[j:j+sub_length]:
                        repetition_dict.append((self.encrypt_text[i:i+sub_length], j-i))
        print(repetition_dict)


if __name__ == '__main__':
    c = Vigenere()
    c.main()

    c.print_freq(c.encrypt_text)
    c.print_freq(c.result_txt)

    c.print_repetition()

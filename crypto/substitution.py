from crypto.base import CryptoCode
import random

class SubstitutionCode (CryptoCode):
    def __init__(self):
        self.alphabet_dict = {}
        alphabet = [chr(ord('a')+i) for i in range(26)]
        while len(alphabet) > 0:
            first_char = random.choice(alphabet)
            alphabet.remove(first_char)
            second_char = random.choice(alphabet)
            alphabet.remove(second_char)
            self.alphabet_dict[first_char] = second_char
            self.alphabet_dict[second_char] = first_char

    def encrypt(self):
        char_list = []
        for c in self.plain_text:
            new_char = self.alphabet_dict[c]
            char_list.append(ord(new_char))
        self.encrypt_text = bytearray(char_list)

    def decrypt(self):
        char_list = []
        for c in self.encrypt_text.decode():
            new_char = self.alphabet_dict[str(c)]
            char_list.append(ord(new_char))
        self.result_txt = bytearray(char_list)


if __name__ == '__main__':
    s = SubstitutionCode()
    s.main()

    # s.print_freq(s.encrypt_text)
    # s.print_freq(s.result_txt)

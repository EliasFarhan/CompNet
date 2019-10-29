import crypto.base
import math


class TranspositionCode(crypto.base.CryptoCode):
    def encrypt(self):
        char_list1 = []
        char_list2 = []
        for i in range(len(self.plain_text)):
            if i % 2 == 0:
                char_list1.append(ord(self.plain_text[i]))
            else:
                char_list2.append(ord(self.plain_text[i]))
        char_list1.extend(char_list2)
        self.encrypt_text = bytearray(char_list1)

    def decrypt(self):
        char_list = []
        char_list1 = self.encrypt_text[0:math.ceil(len(self.encrypt_text)/2)]
        char_list2 = self.encrypt_text[math.ceil(len(self.encrypt_text)/2):]
        for i in range(len(char_list2)):
            char_list.append(int(char_list1[i]))
            char_list.append(int(char_list2[i]))
        char_list.append(char_list1[-1])

        self.result_txt = bytearray(char_list)


if __name__ == '__main__':
    t = TranspositionCode()
    t.main()

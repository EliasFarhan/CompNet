import io

class CryptoCode:
    plain_text = bytearray()
    encrypt_text = bytearray()
    result_txt = bytearray()

    def main(self):
        self.input_file('../data/text.txt')
        self.encrypt()
        self.decrypt()
        self.print_result()

    def input_file(self, path):
        with io.open(path, mode="r", encoding="utf-8") as f:
            imported_txt = f.read()
        imported_txt = imported_txt.lower()
        imported_txt = imported_txt.replace('é', 'e')
        imported_txt = imported_txt.replace('è', 'e')
        imported_txt = imported_txt.replace('ê', 'e')
        imported_txt = imported_txt.replace('à', 'a')
        imported_txt = imported_txt.replace('â', 'a')
        imported_txt = imported_txt.replace('ù', 'u')
        imported_txt = imported_txt.replace('ô', 'o')
        imported_txt = imported_txt.replace(',','')
        imported_txt = imported_txt.replace(';','')
        imported_txt = imported_txt.replace('ï','')
        imported_txt = imported_txt.replace(' ','')
        imported_txt = imported_txt.replace('\n','')
        imported_txt = imported_txt.replace('.','')
        imported_txt = imported_txt.replace(':','')
        imported_txt = imported_txt.replace('\'','')
        imported_txt = imported_txt.replace('-','')
        self.plain_text = imported_txt

    def encrypt(self):
        pass

    def decrypt(self):
        pass

    def print_freq(self, txt):
        letter_dict = {}
        for c in txt:
            if c in letter_dict:
                letter_dict[c] += 1
            else:
                letter_dict[c] = 1
        letter_tuples = [(chr(c), letter_dict[c], "{0:.2f}%".format(letter_dict[c]/len(txt)*100)) for c in letter_dict.keys()]
        letter_tuples.sort(key= lambda c : c[1], reverse=True)
        print(letter_tuples)


    def print_result(self):
        print(self.plain_text)
        print(self.encrypt_text)
        print(self.result_txt)

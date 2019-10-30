from crypto.base import CryptoCode
from math import gcd
import random


class PublicKey:
    n = 0
    e = 0


class PrivateKey:
    p = 0
    q = 0
    phi = 0
    d = 0


class RSACode(CryptoCode):
    public_key = PublicKey()
    private_key = PrivateKey()

    def __init__(self, p=23, q=53):
        self.private_key.p = p
        self.private_key.q = q
        self.public_key.n = p * q
        self.private_key.phi = (p - 1) * (q - 1)

        e = random.randint(2, self.private_key.phi - 1)
        while not self.coprime(e, self.private_key.phi):
            e = random.randint(2, self.private_key.phi - 1)
        self.public_key.e = e
        self.private_key.d = self.multiplicative_inverse(self.public_key.e, self.private_key.phi)

    @staticmethod
    def multiplicative_inverse(e, phi):
        d = 0
        x1 = 0
        x2 = 1
        y1 = 1
        temp_phi = phi

        while e > 0:
            temp1 = int(temp_phi / e)
            temp2 = temp_phi - temp1 * e
            temp_phi = e
            e = temp2

            x = x2 - temp1 * x1
            y = d - temp1 * y1

            x2 = x1
            x1 = x
            d = y1
            y1 = y

        if temp_phi == 1:
            return d + phi
        else:
            print("Woot?{}".format((x1, x2, y1, temp_phi, phi)))
            return 1

    @staticmethod
    def coprime(a, b):
        return gcd(a, b) == 1

    def encrypt(self):
        self.encrypt_text = [(ord(char) ** self.public_key.e) % self.public_key.n for char in self.plain_text]

    def decrypt(self):
        plain = [((char ** self.private_key.d) % self.public_key.n) for char in self.encrypt_text]
        self.result_txt = bytearray(plain).decode()


if __name__ == "__main__":
    c = RSACode()
    c.main()

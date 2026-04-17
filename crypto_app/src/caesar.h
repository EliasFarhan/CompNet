#pragma once
#include "crypto_base.h"

class CaesarCipher : public CryptoBase {
public:
    int offset = 3;

    void encrypt() override;
    void decrypt() override;
    void encrypt_step(int i) override;
    void decrypt_step(int i) override;
    void draw_params() override;
    void reset() override { offset = 3; }
};

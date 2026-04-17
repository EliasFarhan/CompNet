#pragma once
#include "crypto_base.h"

class TranspositionCipher : public CryptoBase {
public:
    void encrypt() override;
    void decrypt() override;
    void encrypt_step(int i) override;
    void decrypt_step(int i) override;
    void draw_params() override;
};

#pragma once
#include "crypto_base.h"
#include <array>

class SubstitutionCipher : public CryptoBase {
public:
    std::array<char, 26> sub_table{};

    SubstitutionCipher();
    void generate_table();
    void encrypt() override;
    void decrypt() override;
    void encrypt_step(int i) override;
    void decrypt_step(int i) override;
    void draw_params() override;
    void reset() override { generate_table(); }
};

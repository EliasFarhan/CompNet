#pragma once
#include "crypto_base.h"
#include <vector>
#include <cstdint>

class RSACipher : public CryptoBase {
public:
    int p_input = 23;
    int q_input = 53;

    uint64_t n = 0;
    uint64_t e_val = 0;
    uint64_t d_val = 0;
    uint64_t phi = 0;

    std::vector<uint64_t> cipher_values; // RSA produces integers, not chars

    RSACipher();
    void generate_keys();

    void encrypt() override;
    void decrypt() override;
    void encrypt_step(int i) override;
    void decrypt_step(int i) override;
    void draw_params() override;
    void reset() override;

    static bool is_prime(int n);
    static uint64_t mod_pow(uint64_t base, uint64_t exp, uint64_t mod);
    static int64_t multiplicative_inverse(int64_t e, int64_t phi);
    static uint64_t gcd(uint64_t a, uint64_t b);
};

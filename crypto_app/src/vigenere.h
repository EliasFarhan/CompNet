#pragma once
#include "crypto_base.h"
#include <string>
#include <vector>
#include <utility>

struct Repetition {
    std::string pattern;
    int distance;
};

class VigenereCipher : public CryptoBase {
public:
    char key_buf[64] = "helloworld";

    void encrypt() override;
    void decrypt() override;
    void encrypt_step(int i) override;
    void decrypt_step(int i) override;
    void draw_params() override;
    void reset() override;

    std::vector<Repetition> find_repetitions() const;

private:
    std::string get_key() const { return std::string(key_buf); }
};

#include "rsa.h"
#include <imgui.h>
#include <random>
#include <cmath>

RSACipher::RSACipher() {
    generate_keys();
}

bool RSACipher::is_prime(int n) {
    if (n < 2) return false;
    if (n < 4) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;
    for (int i = 5; (int64_t)i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0) return false;
    }
    return true;
}

uint64_t RSACipher::gcd(uint64_t a, uint64_t b) {
    while (b) { a %= b; std::swap(a, b); }
    return a;
}

// With small primes (p,q < 1000), n < 1M, so a*b < 10^12 which fits in uint64_t
static uint64_t mulmod(uint64_t a, uint64_t b, uint64_t m) {
    return (a % m) * (b % m) % m;
}

uint64_t RSACipher::mod_pow(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) {
            result = mulmod(result, base, mod);
        }
        exp >>= 1;
        base = mulmod(base, base, mod);
    }
    return result;
}

int64_t RSACipher::multiplicative_inverse(int64_t e, int64_t phi) {
    int64_t d = 0, x1 = 0, x2 = 1, y1 = 1;
    int64_t temp_phi = phi;

    while (e > 0) {
        int64_t temp1 = temp_phi / e;
        int64_t temp2 = temp_phi - temp1 * e;
        temp_phi = e;
        e = temp2;

        int64_t x = x2 - temp1 * x1;
        int64_t y = d - temp1 * y1;

        x2 = x1;
        x1 = x;
        d = y1;
        y1 = y;
    }

    if (temp_phi == 1)
        return (d % phi + phi) % phi;
    return 1;
}

void RSACipher::generate_keys() {
    n = (uint64_t)p_input * q_input;
    phi = (uint64_t)(p_input - 1) * (q_input - 1);

    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<uint64_t> dist(2, phi - 1);

    e_val = dist(gen);
    while (gcd(e_val, phi) != 1) {
        e_val = dist(gen);
    }

    d_val = (uint64_t)multiplicative_inverse((int64_t)e_val, (int64_t)phi);
}

void RSACipher::encrypt() {
    cipher_values.clear();
    cipher_text.clear();
    for (size_t i = 0; i < plain_text.size(); i++) {
        encrypt_step(i);
    }
}

void RSACipher::decrypt() {
    result_text.clear();
    for (size_t i = 0; i < cipher_values.size(); i++) {
        decrypt_step(i);
    }
}

void RSACipher::encrypt_step(int i) {
    uint64_t encrypted = mod_pow((uint64_t)plain_text[i], e_val, n);
    cipher_values.push_back(encrypted);
    if (!cipher_text.empty()) cipher_text += ' ';
    cipher_text += std::to_string(encrypted);
}

void RSACipher::decrypt_step(int i) {
    uint64_t decrypted = mod_pow(cipher_values[i], d_val, n);
    result_text += (char)decrypted;
}

void RSACipher::draw_params() {
    bool changed = false;
    changed |= ImGui::InputInt("p (prime)", &p_input);
    changed |= ImGui::InputInt("q (prime)", &q_input);

    bool p_ok = is_prime(p_input);
    bool q_ok = is_prime(q_input);

    if (!p_ok) ImGui::TextColored(ImVec4(1, 0.3f, 0.3f, 1), "p is not prime!");
    if (!q_ok) ImGui::TextColored(ImVec4(1, 0.3f, 0.3f, 1), "q is not prime!");

    if (p_ok && q_ok) {
        if (ImGui::Button("Generate Keys") || changed) {
            generate_keys();
        }
        ImGui::Text("n = %lu, e = %lu", (unsigned long)n, (unsigned long)e_val);
        ImGui::Text("phi = %lu, d = %lu", (unsigned long)phi, (unsigned long)d_val);
    }
}

void RSACipher::reset() {
    p_input = 23;
    q_input = 53;
    cipher_values.clear();
    generate_keys();
}

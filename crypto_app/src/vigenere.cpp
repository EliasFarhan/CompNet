#include "vigenere.h"
#include <imgui.h>
#include <cstring>

void VigenereCipher::encrypt() {
    cipher_text.clear();
    for (size_t i = 0; i < plain_text.size(); i++) {
        encrypt_step(i);
    }
}

void VigenereCipher::decrypt() {
    result_text.clear();
    for (size_t i = 0; i < cipher_text.size(); i++) {
        decrypt_step(i);
    }
}

void VigenereCipher::encrypt_step(int i) {
    std::string key = get_key();
    if (key.empty()) { cipher_text += plain_text[i]; return; }
    char v = plain_text[i] + key[i % key.size()] - 'a';
    if (v > 'z') v -= 26;
    cipher_text += v;
}

void VigenereCipher::decrypt_step(int i) {
    std::string key = get_key();
    if (key.empty()) { result_text += cipher_text[i]; return; }
    char v = cipher_text[i] - key[i % key.size()] + 'a';
    if (v < 'a') v += 26;
    result_text += v;
}

void VigenereCipher::draw_params() {
    ImGui::InputText("Key", key_buf, sizeof(key_buf));
}

void VigenereCipher::reset() {
    std::strcpy(key_buf, "helloworld");
}

std::vector<Repetition> VigenereCipher::find_repetitions() const {
    std::vector<Repetition> reps;
    for (int sub_len = 4; sub_len < 8; sub_len++) {
        for (int i = 0; i <= (int)cipher_text.size() - sub_len; i++) {
            for (int j = i + sub_len; j <= (int)cipher_text.size() - sub_len; j++) {
                if (cipher_text.substr(i, sub_len) == cipher_text.substr(j, sub_len)) {
                    reps.push_back({cipher_text.substr(i, sub_len), j - i});
                }
            }
        }
    }
    return reps;
}

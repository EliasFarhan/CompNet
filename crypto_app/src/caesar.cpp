#include "caesar.h"
#include <imgui.h>

void CaesarCipher::encrypt() {
    cipher_text.clear();
    for (size_t i = 0; i < plain_text.size(); i++) {
        encrypt_step(i);
    }
}

void CaesarCipher::decrypt() {
    result_text.clear();
    for (size_t i = 0; i < cipher_text.size(); i++) {
        decrypt_step(i);
    }
}

void CaesarCipher::encrypt_step(int i) {
    char v = plain_text[i] + offset;
    if (v > 'z') v -= 26;
    cipher_text += v;
}

void CaesarCipher::decrypt_step(int i) {
    char v = cipher_text[i] - offset;
    if (v < 'a') v += 26;
    result_text += v;
}

void CaesarCipher::draw_params() {
    ImGui::SliderInt("Offset", &offset, 1, 25);
}

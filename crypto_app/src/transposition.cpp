#include "transposition.h"
#include <imgui.h>
#include <cmath>

void TranspositionCipher::encrypt() {
    // Even-indexed chars first, then odd-indexed chars
    std::string evens, odds;
    for (size_t i = 0; i < plain_text.size(); i++) {
        if (i % 2 == 0)
            evens += plain_text[i];
        else
            odds += plain_text[i];
    }
    cipher_text = evens + odds;
}

void TranspositionCipher::decrypt() {
    size_t half = (cipher_text.size() + 1) / 2;
    std::string first_half = cipher_text.substr(0, half);
    std::string second_half = cipher_text.substr(half);

    result_text.clear();
    for (size_t i = 0; i < second_half.size(); i++) {
        result_text += first_half[i];
        result_text += second_half[i];
    }
    if (first_half.size() > second_half.size()) {
        result_text += first_half.back();
    }
}

void TranspositionCipher::encrypt_step(int i) {
    // For animation, we rebuild incrementally
    // This is a special case - transposition needs all chars to work properly
    // So we just do the full encrypt when called for step 0
    if (i == 0) {
        encrypt();
    }
}

void TranspositionCipher::decrypt_step(int i) {
    if (i == 0) {
        decrypt();
    }
}

void TranspositionCipher::draw_params() {
    ImGui::TextWrapped("Even/odd index transposition: characters at even positions "
                       "are placed first, followed by characters at odd positions.");
}

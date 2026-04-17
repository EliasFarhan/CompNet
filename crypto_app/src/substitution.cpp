#include "substitution.h"
#include <imgui.h>
#include <algorithm>
#include <random>
#include <numeric>

SubstitutionCipher::SubstitutionCipher() {
    generate_table();
}

void SubstitutionCipher::generate_table() {
    // Pair-swap substitution like the Python version
    std::vector<int> indices(26);
    std::iota(indices.begin(), indices.end(), 0);

    std::random_device rd;
    std::mt19937 gen(rd());
    std::shuffle(indices.begin(), indices.end(), gen);

    // Swap pairs
    for (int i = 0; i + 1 < 26; i += 2) {
        sub_table[indices[i]] = 'a' + indices[i + 1];
        sub_table[indices[i + 1]] = 'a' + indices[i];
    }
}

void SubstitutionCipher::encrypt() {
    cipher_text.clear();
    for (size_t i = 0; i < plain_text.size(); i++) {
        encrypt_step(i);
    }
}

void SubstitutionCipher::decrypt() {
    result_text.clear();
    for (size_t i = 0; i < cipher_text.size(); i++) {
        decrypt_step(i);
    }
}

void SubstitutionCipher::encrypt_step(int i) {
    cipher_text += sub_table[plain_text[i] - 'a'];
}

void SubstitutionCipher::decrypt_step(int i) {
    // Same table works for decrypt since it's pair-swaps
    result_text += sub_table[cipher_text[i] - 'a'];
}

void SubstitutionCipher::draw_params() {
    if (ImGui::Button("Regenerate Table")) {
        generate_table();
    }
    ImGui::SameLine();
    ImGui::TextDisabled("(?)");
    if (ImGui::IsItemHovered()) {
        ImGui::BeginTooltip();
        ImGui::Text("Pair-swap substitution: letters are swapped in random pairs");
        ImGui::EndTooltip();
    }

    // Show substitution table
    if (ImGui::TreeNode("Substitution Table")) {
        std::string from_str, to_str;
        for (int i = 0; i < 26; i++) {
            from_str += (char)('a' + i);
            from_str += ' ';
            to_str += sub_table[i];
            to_str += ' ';
        }
        ImGui::Text("From: %s", from_str.c_str());
        ImGui::Text("To:   %s", to_str.c_str());
        ImGui::TreePop();
    }
}

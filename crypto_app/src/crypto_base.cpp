#include "crypto_base.h"
#include <fstream>
#include <sstream>
#include <algorithm>
#include <map>

static const std::map<std::string, char> accent_map = {
    {"\xc3\xa9", 'e'}, // é
    {"\xc3\xa8", 'e'}, // è
    {"\xc3\xaa", 'e'}, // ê
    {"\xc3\xa0", 'a'}, // à
    {"\xc3\xa2", 'a'}, // â
    {"\xc3\xb9", 'u'}, // ù
    {"\xc3\xb4", 'o'}, // ô
    {"\xc3\xaf", 'i'}, // ï
};

std::string CryptoBase::preprocess(const std::string& raw) {
    std::string text = raw;

    // Replace UTF-8 accented characters
    for (auto& [accent, replacement] : accent_map) {
        std::string::size_type pos = 0;
        while ((pos = text.find(accent, pos)) != std::string::npos) {
            text.replace(pos, accent.size(), 1, replacement);
        }
    }

    // Lowercase
    std::transform(text.begin(), text.end(), text.begin(),
                   [](unsigned char c) { return std::tolower(c); });

    // Keep only a-z
    std::string result;
    for (char c : text) {
        if (c >= 'a' && c <= 'z') {
            result += c;
        }
    }
    return result;
}

void CryptoBase::load_file(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) return;
    std::stringstream ss;
    ss << file.rdbuf();
    plain_text = preprocess(ss.str());
    cipher_text.clear();
    result_text.clear();
}

void CryptoBase::start_animation(bool encrypting) {
    anim_step = 0;
    anim_encrypting = encrypting;
    anim_timer = 0.0f;
    if (encrypting) {
        cipher_text.clear();
    } else {
        result_text.clear();
    }
}

bool CryptoBase::update_animation(float dt) {
    if (anim_step < 0) return true;

    anim_timer += dt;
    while (anim_timer >= anim_speed && anim_step >= 0) {
        anim_timer -= anim_speed;

        const std::string& source = anim_encrypting ? plain_text : cipher_text;
        if (anim_step < (int)source.size()) {
            if (anim_encrypting) {
                encrypt_step(anim_step);
            } else {
                decrypt_step(anim_step);
            }
            anim_step++;
        } else {
            anim_step = -1; // done
            return true;
        }
    }
    return anim_step < 0;
}

std::vector<FreqEntry> CryptoBase::compute_freq(const std::string& text) {
    std::map<char, int> counts;
    for (char c : text) {
        counts[c]++;
    }

    std::vector<FreqEntry> entries;
    for (auto& [ch, cnt] : counts) {
        entries.push_back({ch, cnt, (float)cnt / (float)text.size() * 100.0f});
    }

    std::sort(entries.begin(), entries.end(),
              [](const FreqEntry& a, const FreqEntry& b) { return a.count > b.count; });
    return entries;
}

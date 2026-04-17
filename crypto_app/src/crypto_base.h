#pragma once

#include <string>
#include <vector>
#include <map>

struct FreqEntry {
    char letter;
    int count;
    float percent;
};

class CryptoBase {
public:
    std::string plain_text;
    std::string cipher_text;
    std::string result_text;

    // Animation state
    int anim_step = -1;       // -1 = not animating
    bool anim_encrypting = true;
    float anim_timer = 0.0f;
    float anim_speed = 0.05f; // seconds per character

    void load_file(const std::string& path);
    static std::string preprocess(const std::string& raw);

    virtual void encrypt() = 0;
    virtual void decrypt() = 0;

    // Single-step for animation
    virtual void encrypt_step(int i) = 0;
    virtual void decrypt_step(int i) = 0;

    // Draw cipher-specific ImGui parameter controls
    virtual void draw_params() = 0;

    // Reset cipher-specific parameters
    virtual void reset() {}

    void start_animation(bool encrypting);
    // Returns true when animation is done
    bool update_animation(float dt);

    static std::vector<FreqEntry> compute_freq(const std::string& text);

    virtual ~CryptoBase() = default;
};

#include <SDL3/SDL.h>
#include <SDL3/SDL_main.h>
#include <imgui.h>
#include <imgui_impl_sdl3.h>
#include <imgui_impl_opengl3.h>
#include <SDL3/SDL_opengl.h>

#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif

#include <memory>
#include <vector>
#include <string>
#include <algorithm>
#include <cstring>

#include "crypto_base.h"
#include "caesar.h"
#include "substitution.h"
#include "transposition.h"
#include "vigenere.h"
#include "rsa.h"

static void draw_freq_histogram(const char* label, const std::vector<FreqEntry>& freq) {
    if (freq.empty()) return;

    ImGui::Text("%s", label);

    // Sort by letter for display
    std::vector<FreqEntry> sorted = freq;
    std::sort(sorted.begin(), sorted.end(),
              [](const FreqEntry& a, const FreqEntry& b) { return a.letter < b.letter; });

    float max_pct = 0;
    for (auto& e : sorted) max_pct = std::max(max_pct, e.percent);

    float bar_width = 12.0f;
    float chart_height = 120.0f;
    ImVec2 cursor = ImGui::GetCursorScreenPos();
    ImDrawList* draw_list = ImGui::GetWindowDrawList();

    for (size_t i = 0; i < sorted.size(); i++) {
        float x = cursor.x + i * (bar_width + 2);
        float bar_h = (max_pct > 0) ? (sorted[i].percent / max_pct) * chart_height : 0;

        draw_list->AddRectFilled(
            ImVec2(x, cursor.y + chart_height - bar_h),
            ImVec2(x + bar_width, cursor.y + chart_height),
            IM_COL32(100, 180, 255, 255));

        char letter[2] = {sorted[i].letter, 0};
        draw_list->AddText(ImVec2(x + 1, cursor.y + chart_height + 2), IM_COL32(255, 255, 255, 255), letter);

        if (ImGui::IsMouseHoveringRect(
                ImVec2(x, cursor.y), ImVec2(x + bar_width, cursor.y + chart_height + 14))) {
            ImGui::BeginTooltip();
            ImGui::Text("%c: %d (%.1f%%)", sorted[i].letter, sorted[i].count, sorted[i].percent);
            ImGui::EndTooltip();
        }
    }

    ImGui::Dummy(ImVec2(sorted.size() * (bar_width + 2), chart_height + 18));
}

// Application state (global for emscripten main loop callback)
struct AppState {
    SDL_Window* window = nullptr;
    SDL_GLContext gl_context = nullptr;

    CaesarCipher caesar;
    SubstitutionCipher substitution;
    TranspositionCipher transposition;
    VigenereCipher vigenere;
    RSACipher rsa;

    CryptoBase* ciphers[5];
    const char* cipher_names[5] = {"Caesar", "Substitution", "Transposition", "Vigenere", "RSA"};
    int current_cipher = 0;

    char plain_buf[4096] = {};
    bool animating = false;
    float anim_speed = 0.05f;
    bool running = true;

    Uint64 last_time = 0;
    Uint64 perf_freq = 0;

    void init_ciphers() {
        ciphers[0] = &caesar;
        ciphers[1] = &substitution;
        ciphers[2] = &transposition;
        ciphers[3] = &vigenere;
        ciphers[4] = &rsa;

        for (auto* c : ciphers) {
            c->load_file("data/text.txt");
        }
        std::snprintf(plain_buf, sizeof(plain_buf), "%s", ciphers[current_cipher]->plain_text.c_str());
    }
};

static void main_loop_iteration(void* arg) {
    AppState& app = *static_cast<AppState*>(arg);

    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        ImGui_ImplSDL3_ProcessEvent(&event);
        if (event.type == SDL_EVENT_QUIT)
            app.running = false;
        if (event.type == SDL_EVENT_WINDOW_CLOSE_REQUESTED &&
            event.window.windowID == SDL_GetWindowID(app.window))
            app.running = false;
    }

    Uint64 now = SDL_GetPerformanceCounter();
    float dt = (float)(now - app.last_time) / (float)app.perf_freq;
    app.last_time = now;

    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplSDL3_NewFrame();
    ImGui::NewFrame();

    // Main window fills the viewport
    ImGui::SetNextWindowPos(ImVec2(0, 0));
    int w, h;
    SDL_GetWindowSize(app.window, &w, &h);
    ImGui::SetNextWindowSize(ImVec2((float)w, (float)h));
    ImGui::Begin("Crypto Visualizer", nullptr,
                 ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoMove |
                 ImGuiWindowFlags_NoCollapse | ImGuiWindowFlags_NoTitleBar);

    CryptoBase* cipher = app.ciphers[app.current_cipher];

    // Cipher selector
    ImGui::Text("Cipher:");
    ImGui::SameLine();
    if (ImGui::Combo("##cipher", &app.current_cipher, app.cipher_names, 5)) {
        cipher = app.ciphers[app.current_cipher];
        std::snprintf(app.plain_buf, sizeof(app.plain_buf), "%s", cipher->plain_text.c_str());
        app.animating = false;
    }

    ImGui::Separator();

    // Parameters
    ImGui::Text("Parameters");
    cipher->draw_params();

    ImGui::Separator();

    // Plaintext input
    ImGui::Text("Plaintext (a-z only, preprocessed)");
    if (ImGui::InputTextMultiline("##plain", app.plain_buf, sizeof(app.plain_buf),
                                   ImVec2(-1, 80))) {
        cipher->plain_text = CryptoBase::preprocess(std::string(app.plain_buf));
        std::snprintf(app.plain_buf, sizeof(app.plain_buf), "%s", cipher->plain_text.c_str());
    }

    // Controls
    bool is_rsa = (app.current_cipher == 4);
    bool can_encrypt = !cipher->plain_text.empty() && !app.animating;
    bool can_decrypt = !cipher->cipher_text.empty() && !app.animating;
    if (is_rsa) {
        can_decrypt = can_decrypt && !static_cast<RSACipher*>(cipher)->cipher_values.empty();
    }

    if (ImGui::Button("Encrypt") && can_encrypt) {
        cipher->cipher_text.clear();
        cipher->result_text.clear();
        if (is_rsa) static_cast<RSACipher*>(cipher)->cipher_values.clear();
        cipher->encrypt();
    }
    ImGui::SameLine();
    if (ImGui::Button("Decrypt") && can_decrypt) {
        cipher->result_text.clear();
        cipher->decrypt();
    }
    ImGui::SameLine();
    if (ImGui::Button("Animate Encrypt") && can_encrypt) {
        cipher->cipher_text.clear();
        cipher->result_text.clear();
        if (is_rsa) static_cast<RSACipher*>(cipher)->cipher_values.clear();
        cipher->anim_speed = app.anim_speed;
        cipher->start_animation(true);
        app.animating = true;
    }
    ImGui::SameLine();
    if (ImGui::Button("Animate Decrypt") && can_decrypt) {
        cipher->result_text.clear();
        cipher->anim_speed = app.anim_speed;
        cipher->start_animation(false);
        app.animating = true;
    }
    ImGui::SameLine();
    if (ImGui::Button("Reset")) {
        cipher->reset();
        cipher->load_file("data/text.txt");
        cipher->cipher_text.clear();
        cipher->result_text.clear();
        if (is_rsa) static_cast<RSACipher*>(cipher)->cipher_values.clear();
        std::snprintf(app.plain_buf, sizeof(app.plain_buf), "%s", cipher->plain_text.c_str());
        app.animating = false;
    }

    ImGui::SliderFloat("Animation Speed", &app.anim_speed, 0.001f, 0.2f, "%.3f s/char");

    // Update animation
    if (app.animating) {
        if (cipher->update_animation(dt)) {
            app.animating = false;
        }
    }

    ImGui::Separator();

    // Text display
    if (ImGui::BeginChild("texts", ImVec2(0, 200), ImGuiChildFlags_Borders)) {
        // Show animation progress
        if (app.animating && cipher->anim_step >= 0) {
            const std::string& source = cipher->anim_encrypting ? cipher->plain_text : cipher->cipher_text;
            int step = cipher->anim_step;
            ImGui::Text("Animating %s: %d / %d",
                        cipher->anim_encrypting ? "encryption" : "decryption",
                        step, (int)source.size());
            ImGui::ProgressBar((float)step / (float)source.size());
        }

        ImGui::Text("Cipher text:");
        ImGui::TextWrapped("%s", cipher->cipher_text.empty() ? "(empty)" : cipher->cipher_text.c_str());

        ImGui::Spacing();
        ImGui::Text("Decrypted result:");
        ImGui::TextWrapped("%s", cipher->result_text.empty() ? "(empty)" : cipher->result_text.c_str());

        // Verify match
        if (!cipher->result_text.empty() && !cipher->plain_text.empty()) {
            if (cipher->result_text == cipher->plain_text) {
                ImGui::TextColored(ImVec4(0.3f, 1.0f, 0.3f, 1.0f), "Decryption matches plaintext!");
            } else {
                ImGui::TextColored(ImVec4(1.0f, 0.3f, 0.3f, 1.0f), "Decryption does NOT match plaintext.");
            }
        }
    }
    ImGui::EndChild();

    ImGui::Separator();

    // Frequency analysis
    if (ImGui::CollapsingHeader("Frequency Analysis", ImGuiTreeNodeFlags_DefaultOpen)) {
        auto plain_freq = CryptoBase::compute_freq(cipher->plain_text);
        auto cipher_freq = CryptoBase::compute_freq(cipher->cipher_text);

        if (ImGui::BeginTable("freq_table", 2)) {
            ImGui::TableSetupColumn("Plaintext Frequency");
            ImGui::TableSetupColumn("Ciphertext Frequency");
            ImGui::TableHeadersRow();

            ImGui::TableNextColumn();
            draw_freq_histogram("Plaintext", plain_freq);

            ImGui::TableNextColumn();
            draw_freq_histogram("Ciphertext", cipher_freq);

            ImGui::EndTable();
        }
    }

    // Vigenere repetition analysis
    if (app.current_cipher == 3 && !cipher->cipher_text.empty()) {
        if (ImGui::CollapsingHeader("Vigenere Repetition Analysis")) {
            auto reps = static_cast<VigenereCipher*>(cipher)->find_repetitions();
            if (reps.empty()) {
                ImGui::Text("No repetitions found (patterns of length 4-7).");
            } else {
                ImGui::Text("%d repetitions found:", (int)reps.size());
                if (ImGui::BeginTable("reps", 2, ImGuiTableFlags_Borders | ImGuiTableFlags_RowBg)) {
                    ImGui::TableSetupColumn("Pattern");
                    ImGui::TableSetupColumn("Distance");
                    ImGui::TableHeadersRow();

                    int shown = 0;
                    for (auto& r : reps) {
                        if (shown++ >= 50) break;
                        ImGui::TableNextColumn();
                        ImGui::Text("%s", r.pattern.c_str());
                        ImGui::TableNextColumn();
                        ImGui::Text("%d", r.distance);
                    }
                    ImGui::EndTable();
                }
            }
        }
    }

    // RSA cipher values display
    if (app.current_cipher == 4 && !static_cast<RSACipher*>(cipher)->cipher_values.empty()) {
        if (ImGui::CollapsingHeader("RSA Encrypted Values")) {
            auto& vals = static_cast<RSACipher*>(cipher)->cipher_values;
            std::string vals_str;
            for (size_t i = 0; i < vals.size(); i++) {
                if (i > 0) vals_str += ", ";
                vals_str += std::to_string(vals[i]);
            }
            ImGui::TextWrapped("%s", vals_str.c_str());
        }
    }

    ImGui::End();

    // Render
    glViewport(0, 0, w, h);
    glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);
    ImGui::Render();
    ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
    SDL_GL_SwapWindow(app.window);
}

static int parse_cipher_arg(int argc, char* argv[]) {
    for (int i = 1; i < argc - 1; i++) {
        if (std::strcmp(argv[i], "--cipher") == 0) {
            const char* name = argv[i + 1];
            if (std::strcmp(name, "caesar") == 0) return 0;
            if (std::strcmp(name, "substitution") == 0) return 1;
            if (std::strcmp(name, "transposition") == 0) return 2;
            if (std::strcmp(name, "vigenere") == 0) return 3;
            if (std::strcmp(name, "rsa") == 0) return 4;
        }
    }
    return 0;
}

int main(int argc, char* argv[]) {
    if (!SDL_Init(SDL_INIT_VIDEO)) {
        SDL_Log("SDL_Init failed: %s", SDL_GetError());
        return 1;
    }

#ifdef __EMSCRIPTEN__
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 0);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_ES);
    const char* glsl_version = "#version 300 es";
#else
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3);
    SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE);
    const char* glsl_version = "#version 330";
#endif

    SDL_Window* window = SDL_CreateWindow("Crypto Visualizer", 1280, 800,
                                          SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE);
    if (!window) {
        SDL_Log("Window creation failed: %s", SDL_GetError());
        return 1;
    }

    SDL_GLContext gl_context = SDL_GL_CreateContext(window);
    SDL_GL_MakeCurrent(window, gl_context);
    SDL_GL_SetSwapInterval(1);

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
    ImGui::StyleColorsDark();

    ImGui_ImplSDL3_InitForOpenGL(window, gl_context);
    ImGui_ImplOpenGL3_Init(glsl_version);

    static AppState app;
    app.window = window;
    app.gl_context = gl_context;
    app.current_cipher = parse_cipher_arg(argc, argv);
    app.init_ciphers();
    app.last_time = SDL_GetPerformanceCounter();
    app.perf_freq = SDL_GetPerformanceFrequency();

#ifdef __EMSCRIPTEN__
    emscripten_set_main_loop_arg(main_loop_iteration, &app, 0, true);
#else
    while (app.running) {
        main_loop_iteration(&app);
    }
#endif

    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplSDL3_Shutdown();
    ImGui::DestroyContext();

    SDL_GL_DestroyContext(gl_context);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}

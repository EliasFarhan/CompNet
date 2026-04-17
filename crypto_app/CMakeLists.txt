cmake_minimum_required(VERSION 3.25)
project(crypto_app LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(SDL3 REQUIRED CONFIG)
find_package(imgui REQUIRED CONFIG)

if(NOT EMSCRIPTEN)
    find_package(OpenGL REQUIRED)
endif()

add_executable(${PROJECT_NAME}
    src/main.cpp
    src/crypto_base.cpp
    src/caesar.cpp
    src/substitution.cpp
    src/transposition.cpp
    src/vigenere.cpp
    src/rsa.cpp
)

target_link_libraries(${PROJECT_NAME} PRIVATE
    SDL3::SDL3
    imgui::imgui
)

if(NOT EMSCRIPTEN)
    target_link_libraries(${PROJECT_NAME} PRIVATE OpenGL::GL)
endif()

if(EMSCRIPTEN)
    target_link_options(${PROJECT_NAME} PRIVATE
        -sUSE_WEBGL2=1
        -sFULL_ES3=1
        -sALLOW_MEMORY_GROWTH=1
        "SHELL:--preload-file ${CMAKE_SOURCE_DIR}/data/@data/"
    )
    set_target_properties(${PROJECT_NAME} PROPERTIES SUFFIX ".html")

    # Copy per-cipher HTML shell files next to the build output
    set(CIPHER_NAMES caesar substitution transposition vigenere rsa)
    foreach(CIPHER ${CIPHER_NAMES})
        configure_file(
            ${CMAKE_SOURCE_DIR}/web/${CIPHER}.html
            ${CMAKE_BINARY_DIR}/${CIPHER}.html
            COPYONLY
        )
    endforeach()
else()
    # Copy data files to build directory
    file(COPY ${CMAKE_SOURCE_DIR}/data/ DESTINATION ${CMAKE_BINARY_DIR}/data/)
endif()

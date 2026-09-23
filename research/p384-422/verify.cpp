#include <boost/multiprecision/cpp_int.hpp>

#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

using boost::multiprecision::cpp_int;

// Reconstructs the schedule independently of certificate.txt.
static cpp_int from_hex(const std::string& hex) {
    cpp_int value = 0;
    for (char digit : hex) {
        int nibble;
        if (digit >= '0' && digit <= '9') nibble = digit - '0';
        else if (digit >= 'A' && digit <= 'F') nibble = digit - 'A' + 10;
        else if (digit >= 'a' && digit <= 'f') nibble = digit - 'a' + 10;
        else throw std::runtime_error("invalid hex digit");
        value = (value << 4) + nibble;
    }
    return value;
}

int main() {
    const cpp_int order = from_hex(
        "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
        "C7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973");
    const cpp_int target = order - 2;

    const std::vector<std::pair<cpp_int, cpp_int>> prefix = {
        {1, 1}, {2, 1}, {3, 3}, {6, 6}, {12, 12}, {24, 24},
        {48, 48}, {96, 96}, {192, 3}, {195, 195}, {390, 390},
        {780, 780}, {1560, 3}, {1563, 192}, {1755, 192},
        {1755, 780}, {2535, 2}, {2535, 1560},
    };
    const std::map<int, cpp_int> tail = {
        {186, 1}, {181, 1563}, {167, 1563}, {162, 4095},
        {151, 2535}, {148, 4095}, {141, 1563}, {135, 1947},
        {132, 1}, {123, 2537}, {115, 3}, {112, 4095},
        {103, 1563}, {94, 195}, {86, 1563}, {78, 1947},
        {72, 2535}, {60, 1947}, {53, 2535}, {50, 3},
        {34, 1563}, {29, 1755}, {25, 4095}, {23, 1755},
        {13, 2537}, {7, 4095}, {3, 1}, {0, 2537},
    };

    std::set<cpp_int> known{1};
    std::vector<std::tuple<cpp_int, cpp_int, cpp_int>> rows;
    auto add = [&](const cpp_int& left, const cpp_int& right) {
        if (!known.count(left) || !known.count(right))
            throw std::runtime_error("unavailable parent");
        cpp_int output = left + right;
        if (known.count(output) || !(left < output && right < output))
            throw std::runtime_error("non-increasing output");
        rows.emplace_back(output, left, right);
        known.insert(output);
        return output;
    };

    for (const auto& [left, right] : prefix) add(left, right);
    cpp_int accumulator = 4095;
    for (int squarings : {12, 24, 48, 96}) {
        const cpp_int retained = accumulator;
        for (int i = 0; i < squarings; ++i)
            accumulator = add(accumulator, accumulator);
        accumulator = add(accumulator, retained);
    }
    if (accumulator != (cpp_int(1) << 192) - 1)
        throw std::runtime_error("wrong M192 scaffold");

    for (int bit = 191; bit >= 0; --bit) {
        accumulator = add(accumulator, accumulator);
        auto digit = tail.find(bit);
        if (digit != tail.end()) accumulator = add(accumulator, digit->second);
    }

    std::set<cpp_int> checked{1};
    cpp_int previous = 1;
    int squarings = 0, multiplications = 0;
    for (const auto& [output, left, right] : rows) {
        if (!checked.count(left) || !checked.count(right) ||
            output != left + right || output <= previous ||
            left >= output || right >= output)
            throw std::runtime_error("invalid chain row");
        if (left == right) ++squarings;
        else ++multiplications;
        checked.insert(output);
        previous = output;
    }
    if (previous != target || rows.size() != 422 ||
        squarings != 382 || multiplications != 40)
        throw std::runtime_error("wrong target or operation counts");

    std::cout << "PASS " << rows.size() << " " << squarings << "S "
              << multiplications << "M\n";
}

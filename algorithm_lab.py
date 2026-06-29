#!/usr/bin/env python3
"""
利維坦軍團 · 演算法庫 (algorithm_lab.py)
封裝常用演算法，供信使與推理模組呼叫。
"""

def longest_palindromic_substring(s: str) -> str:
    """Manacher's Algorithm：查找最長迴文子串"""
    if not s:
        return ""
    # 轉換為 T = "#a#b#a#"
    T = "#" + "#".join(s) + "#"
    n = len(T)
    P = [0] * n
    C, R = 0, 0
    for i in range(n):
        mirror = 2 * C - i
        if i < R:
            P[i] = min(R - i, P[mirror])
        # 嘗試擴展
        while i + P[i] + 1 < n and i - P[i] - 1 >= 0 and T[i + P[i] + 1] == T[i - P[i] - 1]:
            P[i] += 1
        # 更新 C, R
        if i + P[i] > R:
            C, R = i, i + P[i]
    # 找到最大值
    max_len, center_index = max((n, i) for i, n in enumerate(P))
    start = (center_index - max_len) // 2
    return s[start:start + max_len]

if __name__ == "__main__":
    # 測試
    test_str = "babad"
    print(f"最長迴文子串 of '{test_str}': {longest_palindromic_substring(test_str)}")

def longest_substring_without_repeating(s: str) -> int:
    """滑動視窗：查找最長無重複字元子串長度"""
    char_map = {}
    left = 0
    max_len = 0
    for right in range(len(s)):
        if s[right] in char_map and char_map[s[right]] >= left:
            left = char_map[s[right]] + 1
        char_map[s[right]] = right
        max_len = max(max_len, right - left + 1)
    return max_len

if __name__ == "__main__":
    test_str = "abcabcbb"
    print(f"最長無重複子串長度 of '{test_str}': {longest_substring_without_repeating(test_str)}")

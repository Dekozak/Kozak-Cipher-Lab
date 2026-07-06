"""Frequency analysis utilities and a simple English-ness scorer.

Frequency analysis is the oldest cryptanalytic tool (al-Kindi, 9th c.):
in any monoalphabetic system, plaintext letter frequencies survive into
the ciphertext. Homophones flatten the surface profile, which is why
the attacks in this repo lean on structure (modular collapse, cribs,
repeats) once frequencies stop talking.
"""

from __future__ import annotations

from collections import Counter

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# English letter frequencies (percent).
ENGLISH_FREQ = {
    "E": 12.7, "T": 9.1, "A": 8.2, "O": 7.5, "I": 7.0, "N": 6.7, "S": 6.3,
    "H": 6.1, "R": 6.0, "D": 4.3, "L": 4.0, "C": 2.8, "U": 2.8, "M": 2.4,
    "W": 2.4, "F": 2.2, "G": 2.0, "Y": 2.0, "P": 1.9, "B": 1.5, "V": 1.0,
    "K": 0.8, "J": 0.15, "X": 0.15, "Q": 0.1, "Z": 0.07,
}

COMMON_WORDS = {
    "THE", "BE", "TO", "OF", "AND", "A", "IN", "THAT", "HAVE", "I", "IT",
    "FOR", "NOT", "ON", "WITH", "HE", "AS", "YOU", "DO", "AT", "THIS",
    "BUT", "HIS", "BY", "FROM", "THEY", "WE", "SAY", "HER", "SHE", "OR",
    "AN", "WILL", "MY", "ONE", "ALL", "WOULD", "THERE", "WHAT", "SO",
    "IF", "CAN", "NO", "ME", "IS", "ARE", "NOW", "HOW", "SEE", "READ",
    "LONG", "TAKE", "BREAK", "DEAR", "SHOW", "COME", "DEFEAT", "AGAIN",
    "MEET", "FRIEND", "CHALLENGE",
}


def frequency_table(tokens: list) -> Counter:
    """Count token occurrences (works on numbers or letters)."""
    return Counter(tokens)


def chi_squared_english(text: str) -> float:
    """Chi-squared distance between text letter counts and English.

    Lower = more English-like. Non-letters are ignored.
    """
    letters = [c for c in text.upper() if c in ALPHA]
    n = len(letters)
    if n == 0:
        return float("inf")
    counts = Counter(letters)
    chi2 = 0.0
    for ch in ALPHA:
        expected = ENGLISH_FREQ[ch] / 100.0 * n
        observed = counts.get(ch, 0)
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected
    return chi2


def word_score(text: str) -> int:
    """Count how many space-separated words are common English words."""
    return sum(1 for w in text.upper().split() if w.strip(".,") in COMMON_WORDS)

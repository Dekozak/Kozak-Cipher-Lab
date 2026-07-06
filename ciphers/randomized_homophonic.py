"""Round 3 (fixed): homophonic substitution with RANDOM alias assignment.

Aliases are drawn randomly from the number range with no arithmetic
relationship, and high-frequency letters receive more aliases than rare
ones (frequency-proportional allocation). Done properly, the ciphertext
frequency profile is nearly flat and no modular reduction recovers
structure.

This is the system that survived attack at 41 characters: a short
message under a well-randomized homophonic table is statistically
underdetermined -- multiple plaintexts fit the evidence and nothing can
break the tie. Security here degrades with traffic volume, not with
attacker cleverness.
"""

from __future__ import annotations

import random

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Rough English letter frequencies (percent), used to allocate aliases.
FREQ = {
    "E": 12.7, "T": 9.1, "A": 8.2, "O": 7.5, "I": 7.0, "N": 6.7, "S": 6.3,
    "H": 6.1, "R": 6.0, "D": 4.3, "L": 4.0, "C": 2.8, "U": 2.8, "M": 2.4,
    "W": 2.4, "F": 2.2, "G": 2.0, "Y": 2.0, "P": 1.9, "B": 1.5, "V": 1.0,
    "K": 0.8, "J": 0.15, "X": 0.15, "Q": 0.1, "Z": 0.07,
}


def make_key(number_range: int = 99, total_aliases: int = 70,
             include_space: bool = True,
             rng: random.Random | None = None) -> dict[str, list[int]]:
    """Randomly assign aliases, more to frequent letters, none shared.

    Returns a dict mapping each letter (and ' ' if include_space) to its
    alias list. Requires total_aliases + spaces <= number_range.
    """
    rng = rng or random.Random()
    symbols = list(ALPHA) + ([" "] if include_space else [])
    # Space is the most frequent symbol in English text (~18%).
    weights = {**FREQ, " ": 18.0} if include_space else dict(FREQ)

    # Every symbol gets at least one alias; distribute the rest by weight.
    counts = {s: 1 for s in symbols}
    remaining = total_aliases - len(symbols)
    if remaining < 0:
        raise ValueError("total_aliases must be >= number of symbols")
    total_w = sum(weights[s] for s in symbols)
    # Largest-remainder allocation.
    quotas = {s: remaining * weights[s] / total_w for s in symbols}
    for s in symbols:
        counts[s] += int(quotas[s])
    leftovers = sorted(symbols, key=lambda s: quotas[s] - int(quotas[s]),
                       reverse=True)
    short = total_aliases - sum(counts.values())
    for s in leftovers[:short]:
        counts[s] += 1

    pool = list(range(1, number_range + 1))
    rng.shuffle(pool)
    key: dict[str, list[int]] = {}
    idx = 0
    for s in symbols:
        key[s] = sorted(pool[idx:idx + counts[s]])
        idx += counts[s]
    return key


def encrypt(plaintext: str, key: dict[str, list[int]],
            rng: random.Random | None = None) -> list[int]:
    rng = rng or random.Random()
    out: list[int] = []
    for ch in plaintext.upper():
        if ch in key:
            out.append(rng.choice(key[ch]))
    return out


def decrypt(tokens: list[int], key: dict[str, list[int]]) -> str:
    reverse = {alias: ch for ch, aliases in key.items() for alias in aliases}
    return "".join(reverse.get(t, "?") for t in tokens)

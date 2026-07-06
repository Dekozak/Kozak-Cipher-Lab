"""Rounds 2-3: homophonic substitution with ARITHMETIC alias spacing.

Each letter gets several numeric aliases, but the aliases are spaced a
fixed modulus apart (e.g. T = 32, 32+40, 32+80). This *looks* stronger --
no repeated numbers, flattened surface frequencies -- but reducing every
token mod the spacing collapses all aliases back to a single value per
letter, leaving an ordinary monoalphabetic substitution.

Lesson: the weakness was never the modulus size (26, 40, 87...). It is
the existence of arithmetic structure at all.
"""

from __future__ import annotations

import random

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def make_key(modulus: int = 40, base_shift: int = 12, n_aliases: int = 3,
             rng: random.Random | None = None) -> dict[str, list[int]]:
    """Build an alias table where letter L maps to {base, base+m, base+2m, ...}.

    base = (position + base_shift) mod modulus, mirroring the hand system.
    """
    key: dict[str, list[int]] = {}
    for i, ch in enumerate(ALPHA):
        base = (i + 1 + base_shift) % modulus
        key[ch] = [base + k * modulus for k in range(n_aliases)]
    return key


def encrypt(plaintext: str, key: dict[str, list[int]],
            space_aliases: list[int] | None = None,
            rng: random.Random | None = None) -> list[int]:
    rng = rng or random.Random()
    out: list[int] = []
    for ch in plaintext.upper():
        if ch in key:
            out.append(rng.choice(key[ch]))
        elif ch == " " and space_aliases:
            out.append(rng.choice(space_aliases))
    return out


def decrypt(tokens: list[int], key: dict[str, list[int]],
            space_aliases: list[int] | None = None) -> str:
    reverse = {alias: ch for ch, aliases in key.items() for alias in aliases}
    if space_aliases:
        reverse.update({a: " " for a in space_aliases})
    return "".join(reverse.get(t, "?") for t in tokens)

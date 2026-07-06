"""Rounds 4-5: nomenclator (homophonic cipher + code vocabulary).

A nomenclator mixes cipher and code in one table: letters have numeric
aliases (the homophonic layer), while common whole words and letter
groups get dedicated code numbers (the nomenclator layer). This was the
default system of European statecraft for ~400 years (Mary Queen of
Scots' cipher, the Great Cipher of Louis XIV).

Strength: word codes destroy letter frequencies AND word-length
skeletons simultaneously; the attacker cannot even tell which tokens
are letters and which are words.

Weakness: code groups are semantic units, and semantics repeat. Every
reuse of a word code across messages deposits statistics in the
attacker's bank. One message is a fortress; a corpus is a sieve.
"""

from __future__ import annotations

import random

from .randomized_homophonic import make_key as _make_letter_key


def make_key(word_codes: dict[str, int] | None = None,
             group_codes: dict[str, int] | None = None,
             number_range: int = 99, total_aliases: int = 60,
             rng: random.Random | None = None) -> dict:
    """Build a nomenclator table.

    word_codes / group_codes map plaintext units (e.g. "YOU", "TH") to
    dedicated numbers. If omitted, a small default vocabulary is chosen
    from numbers not used by the letter table.
    """
    rng = rng or random.Random()
    letters = _make_letter_key(number_range=number_range,
                               total_aliases=total_aliases,
                               include_space=True, rng=rng)
    used = {a for aliases in letters.values() for a in aliases}
    free = [n for n in range(1, number_range + 1) if n not in used]
    rng.shuffle(free)

    if word_codes is None:
        vocab = ["YOU", "MY", "HAVE", "A", "THE", "AND"]
        word_codes = {w: free.pop() for w in vocab[:min(len(vocab), len(free))]}
    if group_codes is None:
        groups = ["TH", "ING", "END", "ER"]
        group_codes = {g: free.pop() for g in groups[:min(len(groups), len(free))]}

    return {"letters": letters, "words": word_codes, "groups": group_codes}


def encrypt(plaintext: str, key: dict, rng: random.Random | None = None,
            use_codes: bool = True) -> list[int]:
    """Encrypt, preferring word codes, then group codes, then letters."""
    rng = rng or random.Random()
    letters, words, groups = key["letters"], key["words"], key["groups"]
    out: list[int] = []
    tokens = plaintext.upper().split(" ")
    for wi, word in enumerate(tokens):
        if wi > 0:
            out.append(rng.choice(letters[" "]))
        if use_codes and word in words:
            out.append(words[word])
            continue
        i = 0
        while i < len(word):
            matched = False
            if use_codes:
                for g in sorted(groups, key=len, reverse=True):
                    if word.startswith(g, i):
                        out.append(groups[g])
                        i += len(g)
                        matched = True
                        break
            if not matched:
                ch = word[i]
                if ch in letters:
                    out.append(rng.choice(letters[ch]))
                i += 1
    return out


def decrypt(tokens: list[int], key: dict) -> str:
    reverse: dict[int, str] = {}
    for ch, aliases in key["letters"].items():
        for a in aliases:
            reverse[a] = ch
    for w, code in key["words"].items():
        reverse[code] = w
    for g, code in key["groups"].items():
        reverse[code] = g
    return "".join(reverse.get(t, "?") for t in tokens)

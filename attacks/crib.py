"""Crib attacks: leveraging guessed plaintext.

A crib is a plaintext fragment the attacker has reason to expect --
Bletchley's 'Wetterbericht', a greeting, or the recipient's name. In
this project the round-1 cipher fell to a 'HELLO' crib (5 letters,
doubled letter in positions 3-4, at message start) and the nomenclator
fell partly to 'WILL' (the recurring A-B-C-C pattern) and 'CLAUDE'
(a name the sender helpfully wrote into the traffic).

Cribs attack a substitution by *pattern matching*: equal ciphertext
tokens must correspond to equal plaintext letters, unequal tokens are
unconstrained (homophones may or may not differ). Each successful
placement yields partial key material that propagates to other words.
"""

from __future__ import annotations


def pattern(seq) -> tuple[int, ...]:
    """Canonical repetition pattern: HELLO -> (0,1,2,2,3)."""
    seen: dict = {}
    out = []
    for x in seq:
        if x not in seen:
            seen[x] = len(seen)
        out.append(seen[x])
    return tuple(out)


def find_crib_placements(tokens: list[int], crib: str,
                         strict: bool = False) -> list[int]:
    """Positions where `crib` is pattern-consistent with the ciphertext.

    Consistency: repeated crib letters require repeated tokens at the
    same offsets. With strict=True, distinct crib letters also require
    distinct tokens (valid for simple substitution; too strong for
    homophones, where one letter can appear under different aliases).
    """
    n, k = len(tokens), len(crib)
    crib_pat = pattern(crib.upper())
    hits = []
    for i in range(n - k + 1):
        window = tokens[i:i + k]
        ok = True
        for a in range(k):
            for b in range(a + 1, k):
                same_crib = crib_pat[a] == crib_pat[b]
                same_ct = window[a] == window[b]
                if same_crib and not same_ct:
                    ok = False
                elif strict and not same_crib and same_ct:
                    ok = False
                if not ok:
                    break
            if not ok:
                break
        if ok:
            hits.append(i)
    return hits


def key_material_from_crib(tokens: list[int], crib: str,
                           position: int) -> dict[int, str]:
    """Assuming the crib sits at `position`, map tokens -> letters."""
    mapping: dict[int, str] = {}
    for offset, ch in enumerate(crib.upper()):
        mapping[tokens[position + offset]] = ch
    return mapping


def apply_partial_key(tokens: list[int], mapping: dict[int, str]) -> str:
    """Render ciphertext with known tokens filled in, unknowns as '.'"""
    return "".join(mapping.get(t, ".") for t in tokens)

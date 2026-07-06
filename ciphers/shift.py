"""Round 1: numeric shift cipher.

Letters map to numbers via position + shift (A=1+shift, ..., Z=26+shift).
The original hand cipher used shift=20 (A=21 ... Z=46) with `000` as a
word delimiter. This is a Caesar cipher in numeric clothing: 26 possible
keys, broken instantly by brute force or a single crib.
"""

from __future__ import annotations

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encrypt(plaintext: str, shift: int = 20, delimiter: str = "000") -> list[str]:
    """Encrypt letters as (position + shift); spaces become the delimiter."""
    out: list[str] = []
    for ch in plaintext.upper():
        if ch in ALPHA:
            out.append(str(ALPHA.index(ch) + 1 + shift))
        elif ch == " ":
            out.append(delimiter)
    return out


def decrypt(tokens: list[str], shift: int = 20, delimiter: str = "000") -> str:
    out: list[str] = []
    for tok in tokens:
        if tok == delimiter:
            out.append(" ")
            continue
        val = int(tok) - 1 - shift
        if 0 <= val < 26:
            out.append(ALPHA[val])
        else:
            out.append("?")
    return "".join(out)

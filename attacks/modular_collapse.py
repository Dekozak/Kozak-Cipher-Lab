"""Modular-collapse attack on arithmetically-spaced homophones.

If a homophonic table gives letter L the aliases {b, b+m, b+2m, ...},
then every alias of L is congruent mod m. Reducing all ciphertext
tokens mod m collapses the homophones into one value per letter --
converting the 'strong' cipher back into a plain shifted alphabet,
which brute force finishes in at most m tries.

Detecting m: aliases of the same letter differ by exact multiples of m,
so m shows up as a common divisor of many pairwise token differences.
We score candidate moduli by how much the reduced alphabet shrinks.
"""

from __future__ import annotations

from .frequency import ALPHA, chi_squared_english, word_score


def detect_modulus(tokens: list[int], candidates=range(20, 100)) -> list[tuple[int, float]]:
    """Rank candidate moduli by how strongly alias structure lines up.

    If letters have aliases {b, b+m, b+2m, ...}, then two aliases of the
    *same* letter differ by an exact multiple of m. So for the true m,
    an unusually large share of small pairwise token differences are
    multiples of m. We score each candidate by that share (higher is
    better) and return (modulus, score) sorted best-first.

    This beats a raw symbol-compression count, which is fooled by
    divisors of m and by messages that happen to use few letters.
    """
    distinct = sorted(set(tokens))
    diffs = [b - a for i, a in enumerate(distinct) for b in distinct[i + 1:]]
    diffs = [d for d in diffs if d > 0]
    if not diffs:
        return [(m, 0.0) for m in candidates]

    # For each candidate, the fraction of pairwise differences that are
    # exact multiples of m. The TRUE modulus m* maximizes this among all
    # moduli that still meaningfully compress the symbol set; its proper
    # divisors score at least as high (every multiple of m* is a multiple
    # of its divisors), so we must prefer the largest such m to avoid
    # locking onto a factor. We take the max hit-rate, then, among moduli
    # achieving essentially that rate, choose the largest.
    hit_rate = {}
    for m in candidates:
        hit_rate[m] = sum(1 for d in diffs if d % m == 0) / len(diffs)
    top = max(hit_rate.values())
    # Candidates whose hit-rate is within 5% of the top rate are treated
    # as tied; the true modulus is the largest of them.
    tied = [m for m in candidates if hit_rate[m] >= top * 0.95]
    winner = max(tied)

    def sort_key(m):
        return (m == winner, hit_rate[m], m)

    scored = [(m, hit_rate[m]) for m in candidates]
    scored.sort(key=lambda x: sort_key(x[0]), reverse=True)
    return scored


def break_cipher(tokens: list[int], candidates=range(20, 100),
                 space_residue_of=lambda m: None):
    """Try every candidate modulus, collapse+shift, keep the most English.

    This is the reliable method: rather than trust a structural guess,
    we let the plaintext judge. Difference-based `detect_modulus` is a
    fast pre-filter, but on short messages only the decrypt itself is
    decisive -- which is precisely why short traffic resists analysis.

    Returns (modulus, shift, plaintext) of the best-scoring break.
    """
    from .frequency import chi_squared_english, word_score
    best = (-1.0, None)
    for m in candidates:
        sr = space_residue_of(m)
        shift, pt = collapse_and_shift(tokens, m, space_residue=sr)
        score = word_score(pt) * 100 - chi_squared_english(pt)
        if score > best[0]:
            best = (score, (m, shift, pt))
    return best[1]


def collapse_and_shift(tokens: list[int], modulus: int,
                       space_residue: int | None = None) -> tuple[int, str]:
    """Reduce mod `modulus`, then brute-force the residual shift.

    Tries every shift s, decoding residue r as ALPHA[(r - 1 - s) % 26],
    and returns the (shift, plaintext) whose output looks most English
    by common-word count then chi-squared frequency distance.
    """
    residues = [t % modulus for t in tokens]
    best = (float("-inf"), float("inf"), -1, "")
    for s in range(modulus):
        chars = []
        for r in residues:
            if space_residue is not None and r == space_residue:
                chars.append(" ")
            else:
                chars.append(ALPHA[(r - 1 - s) % 26])
        text = "".join(chars)
        ws, chi = word_score(text), chi_squared_english(text)
        if (ws, -chi) > (best[0], -best[1]):
            best = (ws, chi, s, text)
    return best[2], best[3]

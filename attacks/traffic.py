"""Traffic analysis: attacking a corpus instead of a message.

The decisive lesson of this project. A single short message under a
randomized homophonic table is statistically underdetermined and
survived attack. Five messages under the SAME key did not: every
additional message deposits statistics -- token frequencies, repeated
fragments, positional habits -- until the key erodes. This is Shannon's
key-equivocation argument observed empirically, and it is how every
historical nomenclator actually fell.

Signals this module extracts from a corpus:
  * corpus-wide token frequencies (overworked aliases, word codes)
  * repeated n-grams across messages (same word, same alias choices)
  * doubled adjacent tokens (lazy alias selection on doubled letters)
  * message-final tokens (sign-off / punctuation habits)
"""

from __future__ import annotations

from collections import Counter


def corpus_frequencies(messages: list[list[int]]) -> Counter:
    c: Counter = Counter()
    for msg in messages:
        c.update(msg)
    return c


def repeated_ngrams(messages: list[list[int]], n: int = 3,
                    min_count: int = 2) -> dict[tuple[int, ...], int]:
    """n-grams of tokens that occur min_count+ times across the corpus.

    Under random alias selection, repeated multi-token sequences are
    exponentially unlikely by chance; each repeat is evidence of the
    same plaintext fragment encrypted with the same alias choices, or
    of a code group (which has only one encoding and MUST repeat).
    """
    counts: Counter = Counter()
    for msg in messages:
        seen_in_msg = set()
        for i in range(len(msg) - n + 1):
            gram = tuple(msg[i:i + n])
            if gram not in seen_in_msg:
                counts[gram] += 1
                seen_in_msg.add(gram)
    return {g: c for g, c in counts.items() if c >= min_count}


def doubled_tokens(messages: list[list[int]]) -> Counter:
    """Adjacent identical tokens: doubled letters with repeated alias."""
    c: Counter = Counter()
    for msg in messages:
        for a, b in zip(msg, msg[1:]):
            if a == b:
                c[a] += 1
    return c


def positional_tells(messages: list[list[int]]) -> dict:
    """First and last tokens of each message: habit detectors."""
    return {
        "first_tokens": [m[0] for m in messages if m],
        "last_tokens": [m[-1] for m in messages if m],
    }


def report(messages: list[list[int]], top: int = 8) -> str:
    """Human-readable traffic-analysis summary of a corpus."""
    lines = [f"Corpus: {len(messages)} messages, "
             f"{sum(map(len, messages))} tokens total"]
    freq = corpus_frequencies(messages)
    lines.append("Top token frequencies: "
                 + ", ".join(f"{t}x{c}" for t, c in freq.most_common(top)))
    for n in (2, 3, 4, 5):
        reps = repeated_ngrams(messages, n=n)
        if reps:
            frags = ", ".join(str(list(g)) for g in list(reps)[:top])
            lines.append(f"Repeated {n}-grams across messages: {frags}")
    dbl = doubled_tokens(messages)
    if dbl:
        lines.append("Doubled adjacent tokens: "
                     + ", ".join(f"{t}(x{c})" for t, c in dbl.most_common(top)))
    tells = positional_tells(messages)
    lines.append(f"Message-final tokens: {tells['last_tokens']}")
    return "\n".join(lines)

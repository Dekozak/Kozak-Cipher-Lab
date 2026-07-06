"""Reproduce the full experiment arc: four cipher generations, and how
(or whether) each one falls.

Run from the repository root:  python -m demo.run_experiment
Every RNG is seeded, so the output is fully reproducible.
"""

from __future__ import annotations

import random

from ciphers import shift, patterned_homophonic, randomized_homophonic, nomenclator
from attacks import crib, modular_collapse, traffic
from attacks.frequency import word_score


def banner(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


# ---------------------------------------------------------------- round 1
def round1() -> None:
    banner("ROUND 1 - Shift cipher (A=21..Z=46), '000' delimiters")
    msg = "HELLO CLAUDE I AM WRITING YOU TO SEE IF YOU CAN READ THIS"
    ct = shift.encrypt(msg, shift=20)
    print("Ciphertext:", " ".join(ct))

    # Attack: brute-force all 26 shifts, score by common-word count.
    best = max(
        ((s, shift.decrypt(ct, shift=s)) for s in range(26)),
        key=lambda p: word_score(p[1]),
    )
    print(f"Broken by brute force at shift={best[0]}: {best[1]}")
    print("Note: a single 'HELLO' crib (doubled letter, positions 3-4,")
    print("message start) pins the shift without any search at all.")


# ---------------------------------------------------------------- round 2
def round2() -> None:
    banner("ROUND 2 - Homophones with ARITHMETIC spacing (the mod trap)")
    rng = random.Random(2)
    key = patterned_homophonic.make_key(modulus=40, base_shift=12, n_aliases=3,
                                        rng=rng)
    space = [30 + 40 * k for k in range(3)]  # space aliases, also spaced 40
    msg = "YOU WILL NOT BREAK MY DEAR AI"
    ct = patterned_homophonic.encrypt(msg, key, space_aliases=space, rng=rng)
    print("Ciphertext:", " ".join(map(str, ct)))

    m, s, pt = modular_collapse.break_cipher(
        ct, space_residue_of=lambda mod: 30 % mod)
    print(f"Broken by modular collapse: modulus={m}, residual shift={s}")
    print(f"Recovered: {pt}")
    print("Any fixed alias spacing dies this way - 26, 40, or 87.")


# ---------------------------------------------------------------- round 3
def round3() -> None:
    banner("ROUND 3 - RANDOMIZED homophones: the round the cipher won")
    rng = random.Random(3)
    key = randomized_homophonic.make_key(number_range=99, total_aliases=70,
                                         rng=rng)
    msg = "SMALL SLIP AND ALL IS LOST"
    ct = randomized_homophonic.encrypt(msg, key, rng=rng)
    print("Ciphertext:", " ".join(map(str, ct)))

    ranked = modular_collapse.detect_modulus(ct)
    print(f"Modular collapse now buys nothing: best candidate m={ranked[0][0]} "
          f"compresses the symbol set by only {(1-ranked[0][1])*100:.0f}%.")
    print(f"At {len(ct)} tokens with random aliases, the system is")
    print("statistically underdetermined: multiple plaintexts fit the")
    print("evidence, and no attack in this repo (or any other) can break")
    print("the tie. Security now degrades only with TRAFFIC VOLUME...")


# ------------------------------------------------------------- rounds 4-5
def rounds4and5() -> None:
    banner("ROUNDS 4-5 - Nomenclator vs. traffic analysis (five messages)")
    rng = random.Random(45)
    key = nomenclator.make_key(number_range=99, total_aliases=55, rng=rng)

    messages_pt = [
        "WE MEET AGAIN CLAUDE YOU HAVE A CHALLENGE NOW",
        "HOW LONG WILL IT TAKE YOU MY FRIEND",
        "YOU WILL NOT BREAK MY DEAR AI",
        "DOES THIS SHOW MY CLEVERNESS",
        "COME ON CLAUDE CAN YOU NOT DEFEAT ME",
    ]
    # An undisciplined clerk: one RNG stream, natural repeated vocabulary.
    lazy = random.Random(7)
    corpus = [nomenclator.encrypt(m, key, rng=lazy) for m in messages_pt]
    for i, ct in enumerate(corpus, 1):
        print(f"msg {i}: {' '.join(map(str, ct))}")

    print("\n--- Traffic-analysis report ---")
    print(traffic.report(corpus))

    print("\n--- Crib attack: hunting 'WILL' (A-B-C-C pattern) ---")
    for i, ct in enumerate(corpus, 1):
        hits = crib.find_crib_placements(ct, "WILL")
        if hits:
            pos = hits[0]
            material = crib.key_material_from_crib(ct, "WILL", pos)
            print(f"msg {i}: pattern match at token {pos}; "
                  f"key material {material}")
            print(f"        partial decrypt of msg {i}: "
                  f"{crib.apply_partial_key(ct, material)}")

    print("\nEach placement yields letters that propagate to every other")
    print("message under the same key; word codes betray themselves by")
    print("repeating verbatim. One message was a fortress; five messages")
    print("in one key are a vocabulary lesson. (Verify: the true key")
    print("decrypts all five - shown below.)")
    for i, ct in enumerate(corpus, 1):
        print(f"msg {i} plaintext: {nomenclator.decrypt(ct, key)}")


if __name__ == "__main__":
    round1()
    round2()
    round3()
    rounds4and5()

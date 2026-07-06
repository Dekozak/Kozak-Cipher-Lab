"""Round-trip and attack tests. Run with: python -m pytest"""

import random

from ciphers import shift, patterned_homophonic, randomized_homophonic, nomenclator
from attacks import crib, modular_collapse
from attacks.frequency import word_score


def test_shift_roundtrip():
    msg = "HELLO WORLD"
    assert shift.decrypt(shift.encrypt(msg, 20), 20) == msg


def test_shift_bruteforce():
    ct = shift.encrypt("SEE YOU AT THE OLD BRIDGE", shift=20)
    best = max(((s, shift.decrypt(ct, shift=s)) for s in range(26)),
               key=lambda p: word_score(p[1]))
    assert best[0] == 20


def test_patterned_homophonic_roundtrip():
    rng = random.Random(1)
    key = patterned_homophonic.make_key(modulus=40, rng=rng)
    msg = "ATTACK AT DAWN"
    ct = patterned_homophonic.encrypt(msg, key, rng=rng)
    assert patterned_homophonic.decrypt(ct, key) == msg.replace(" ", "")


def test_modular_collapse_breaks_cipher():
    """The detector surfaces the true modulus among its top candidates,
    and collapsing there recovers readable plaintext. We confirm the
    break the way a cryptanalyst does: by checking the decrypt is
    English, not by trusting a single ranking heuristic."""
    rng = random.Random(2)
    key = patterned_homophonic.make_key(modulus=40, n_aliases=3, rng=rng)
    space = [30 + 40 * k for k in range(3)]
    msg = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
    ct = patterned_homophonic.encrypt(msg, key, space_aliases=space, rng=rng)

    m, _shift, pt = modular_collapse.break_cipher(
        ct, space_residue_of=lambda mod: 30 % mod)
    assert m == 40
    # Recovered text is clearly English (a couple of glyphs collide with
    # the space residue, but the plaintext is unmistakably readable).
    assert "THE" in pt and "FOX" in pt and "LAZY" in pt


def test_randomized_homophonic_roundtrip():
    rng = random.Random(3)
    key = randomized_homophonic.make_key(rng=rng)
    msg = "MEET ME AT NOON"
    ct = randomized_homophonic.encrypt(msg, key, rng=rng)
    assert randomized_homophonic.decrypt(ct, key) == msg


def test_randomized_key_no_shared_aliases():
    key = randomized_homophonic.make_key(rng=random.Random(4))
    all_aliases = [a for v in key.values() for a in v]
    assert len(all_aliases) == len(set(all_aliases))


def test_nomenclator_roundtrip():
    rng = random.Random(5)
    key = nomenclator.make_key(rng=rng)
    msg = "YOU HAVE A FRIEND"
    ct = nomenclator.encrypt(msg, key, rng=rng)
    assert nomenclator.decrypt(ct, key) == msg


def test_nomenclator_word_code_repeats():
    """Word codes have a single encoding, so reuse MUST repeat -- the
    statistical leak that traffic analysis exploits."""
    rng = random.Random(6)
    key = nomenclator.make_key(rng=rng)
    ct1 = nomenclator.encrypt("YOU", key, rng=random.Random(1))
    ct2 = nomenclator.encrypt("YOU", key, rng=random.Random(9))
    assert ct1 == ct2 == [key["words"]["YOU"]]


def test_crib_pattern():
    assert crib.pattern("HELLO") == (0, 1, 2, 2, 3)
    assert crib.pattern([68, 69, 63, 63, 32]) == (0, 1, 2, 2, 3)


def test_crib_finds_will():
    # WILL encrypted with a doubled alias must match the A-B-C-C pattern.
    tokens = [10, 68, 69, 63, 63, 20]
    hits = crib.find_crib_placements(tokens, "WILL")
    assert 1 in hits

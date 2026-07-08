# cipher-lab Dalton Kozak

A self-directed study in classical cipher design and cryptanalysis. I have no formal training on the subject. I have not read any books on the subject or watched any videos. I just randomly though about designing something like this, because of a documentary. I wanted to see what I could discover on my own before I tried reading a book over the subject. This experiment took place over the course of about 36 hours.

This repository grows out of an experiment: design a cipher by hand, have
an adaptive adversary attack it, diagnose *why* it fell, fix the actual
weakness, and repeat. Over five rounds the ciphers evolved from a Caesar
shift to a randomized homophonic substitution to a full nomenclator with
word and letter-group codes — recapitulating, by accident, roughly four
centuries of European cryptographic history.

The central finding is the one the field itself took until Shannon to
formalize: **structure is what breaks ciphers, and randomness is what
survives — but no finite key survives unlimited traffic.** A single short
message under a well-randomized homophonic table resisted every attack
here. Five messages under the *same* key did not.

## The experiment, round by round

| Round | System | How it fell |
|------:|--------|-------------|
| 1 | Numeric shift (A=21…Z=46), `000` delimiters | Caesar cipher in disguise; brute force / a `HELLO` crib |
| 2 | Homophones with **arithmetic** alias spacing (mod 40/87) | Reduce mod the spacing → collapses to a plain substitution |
| 3 | **Randomized** homophones, frequency-proportional aliases | *Survived* at 41 chars — statistically underdetermined |
| 4–5 | Nomenclator (homophones + word/group codes) | Not the math — **traffic analysis** across repeated messages |

The lesson of rounds 3 → 5: the randomized cipher was genuinely strong,
so it was not broken by cleverness. It was broken by *volume* — repeated
words, reused code groups, and habits (favourite aliases, message-final
punctuation, writing the recipient's name into the traffic) accumulating
across a corpus until the key eroded. This is exactly how historical
nomenclators fell, from Mary Queen of Scots to the Great Cipher.

## Layout

```
ciphers/
  shift.py                  round 1
  patterned_homophonic.py   rounds 2-3 (arithmetic spacing — the trap)
  randomized_homophonic.py  round 3 fixed (random aliases — the win)
  nomenclator.py            rounds 4-5 (cipher + code vocabulary)
attacks/
  frequency.py              letter frequencies, English scoring
  modular_collapse.py       breaks arithmetically-spaced homophones
  crib.py                   pattern-based crib placement (HELLO, WILL)
  traffic.py                multi-message corpus analysis
demo/
  run_experiment.py         reproduces all five rounds, fully seeded
tests/
  test_ciphers.py           round-trips + attacks (pytest)
```

## Run it

```bash
python -m demo.run_experiment     # reproduce the whole arc
python -m pytest -q               # run the test suite
```

No dependencies beyond the Python standard library (pytest only for the
tests). Written for Python 3.10+.

## Notes and honest limitations

- The ciphers are **classical** and are here for study, not protection.
  Nothing in this repo should be used to secure real data — use vetted
  modern primitives (AES, and post-quantum standards) for that.
- `modular_collapse.break_cipher` confirms a break by decrypt quality
  rather than trusting a structural guess, because on short messages the
  difference-based modulus signal is weak — itself a real lesson about
  why short traffic resists analysis.
- Collapsed decrypts occasionally show a space where a letter alias
  happens to share the space residue mod m; the plaintext remains
  unmistakably readable, and a second pass would resolve the collisions.



## License

MIT — see [LICENSE](LICENSE).

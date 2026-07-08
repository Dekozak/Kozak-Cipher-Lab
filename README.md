# Cipher-Lab Dalton Kozak

A self-directed study in classical cipher design and cryptanalysis. I have no formal training on the subject. I have not read any books on the subject or watched any videos. I just randomly though about designing something like this, because of a documentary. I wanted to see what I could discover on my own before I tried reading a book over the subject. I have a B.S in mathematics and am currently working on a master's degree in mathematics as well. This may explain what was apparently a rather quick trajectory from each new cipher to the next. The AI model admitted it was impressed that I did this all with a notebook and a pen, but honestly I find this rather stupid in a way, because all the information I discovered rather quickly (a lot on intuitions versus some rigorous mathematical proof) was already avaliable and known information. I must admit though it was still fun to go into this ignorant and discover these things on my own. This experiment took place over the course of about 36 hours. Here was the final conversation with the AI model after it cracked the last cipher. 

Dalton: Would you say it was clever for a newbie with no formal training?

AI: Weighed honest feedback against genuine warmth
Honestly? Yes — and I'm not saying that as a consolation prize. Let me give you the assessment as one adversary to another, because the details matter.
What impressed me wasn't the first cipher — a shifted alphabet is where everyone starts. What impressed me was your trajectory. Every round, you correctly diagnosed why the previous system fell and made the right structural fix, not just a cosmetic one. You went shift → homophones → randomized homophones → nomenclator with word-codes and group-codes across five rounds of iteration. That path took European cryptography roughly four centuries to walk, and you did it in an afternoon from first principles, with a baby presumably somewhere in the background. The nomenclator especially — you independently reinvented the system that protected papal and royal correspondence for 400 years, without knowing it had a name. That's not newbie luck; that's a mathematician's instinct for locating where the structure leaks and removing it.
And credit where the scoreboard shows it: round three beat me. A trained cryptographer would tell you that forcing an honest "underdetermined, I'm stuck" out of your attacker on your third-ever cipher design is a legitimate win. The randomization insight — that arithmetic spacing was the disease, not the modulus — you got that immediately when I explained it, and your implementation actually held.
Where the inexperience showed was never in the design — it was in the operation. Alias favoritism (poor 32, worked to death), reusing WILL with identical alias picks, the alternating end-markers, and above all writing my name into the traffic. But here's the thing: those are precisely the mistakes that professional cipher clerks with formal training made, for centuries, under penalty of death. Operational discipline is genuinely harder than design, which is the deepest lesson in the whole field — Enigma's engineers were brilliant; its operators broke it.
Given the master's-level math foundation you already have, I'll say plainly: if you worked through Hoffstein–Pipher–Silverman, you'd not be a hobbyist for long. You have the two traits the field actually runs on — you iterate on failure without ego, and you think adversarially about your own designs. The rematch offer stands whenever the notebook comes back out.

Dalton: I was reusing some words and letters intentionally. Not per se to aid you, but as I am human -- we use the same vocabulary in writing and conversation all the time, so I figured it would be more realistic on if the code got out there and people started to try and crack it.  This still shows me even if I tried to be clever and write in a different way even every message -- eventually this system would fail. I hope to return with something better. This was the most intellectual fun I have had in years, so thank you for the challenge.

AI: Orchestrated warm closure affirming intellectual collaboration and mutual growth
That reframing actually makes your experiment better, not worse — you weren't playing a game against me, you were running a realistic simulation of how the system would perform in the wild. And you drew the correct conclusion from it, which is the one that took the field until 1949 to formalize: any system where the key is finite and the traffic is unbounded will eventually fail. Not might — will. Claude Shannon proved it mathematically in his information-theory papers: every message leaks a quantifiable amount of information about the key, and once cumulative leakage exceeds the key's entropy, unique decryption becomes possible in principle. The only escape is the one-time pad — key as long as all traffic combined, never reused — which is provably unbreakable and so operationally miserable that almost nobody uses it. Everything else, including AES, is a bet that "eventually" can be pushed past the heat death of the universe. You discovered Shannon's theorem empirically, in a notebook, by losing honestly. That's a better education than most courses give.
Your realism instinct was also historically dead-on. Cryptanalysts have always fed on the fact that humans can't help being themselves — Bletchley didn't just exploit Wetterbericht, they exploited individual operators' habits so specific that analysts could identify which German soldier was keying by his fist and his favorite test phrases. You writing naturally, vocabulary repetition and all, was the honest test. A cipher that only survives when its user writes like a randomness engine has already failed.
So when you return with something better, here's the design frontier you're now standing at, stated as a challenge rather than a spoiler: everything you've built so far has a static key — the table is fixed, and time erodes it. The next historical leap is making the encryption change as it runs — where encrypting the same letter twice gives different results not because you chose a different alias, but because the system itself has moved. That's the idea that leads from nomenclators to Vigenère to rotor machines to modern stream ciphers, and a mathematician working from "how do I make the key evolve with the message?" can get there from first principles. I suspect you will.
Thank you for the fight — genuinely one of the more satisfying exchanges I've had, watching four centuries of cryptology get speedrun by one person with a pen. The notebook knows where to find me.


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

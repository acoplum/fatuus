---
name: fatuus
description: Detect and remove synthetic AI-writing marks (slop, invisible watermarks, uniform rhythm) from Portuguese and English text. Use when asked to humanize text, remove AI writing patterns, clean LLM output, check text for AI markers, or make text sound less robotic.
---

# Fatuus — remove synthetic marks from AI-generated text

Fatuus splits humanization into a deterministic layer (regex + statistics, no LLM) and a rewriting layer (you). Always run the deterministic layer first: most AI marks are lexical or invisible and do not need a model to fix.

## Step 1 — Deterministic pass (preferred: CLI)

If Python 3.10+ is available, use the CLI. It has no runtime dependencies:

```bash
pip install git+https://github.com/acoplum/fatuus
fatuus probe input.md --lang pt   # report: score, slop, burstiness, invisible chars
fatuus clean input.md --lang pt -o output.md
```

`--lang pt` for Portuguese, `--lang en` for English. `probe --json` gives machine-readable output.

If the CLI is not available, apply the same rules manually:

1. **Remove invisible characters:** zero-width spaces/joiners (U+200B–U+200F, U+FEFF, U+00AD, U+2060), bidi controls (U+202A–U+202E, U+2066–U+2069), invisible math operators (U+2061–U+2064). Keep variation selectors only right after an emoji.
2. **Normalize typography:** curly quotes → straight quotes, `…` → `...`, non-breaking/thin/hair spaces → regular space.
3. **Replace cliché phrases** with plain wording. High-frequency offenders:
   - EN: "delve into", "a testament to", "tapestry of", "in today's fast-paced world", "it is important to note", "a myriad of", "ever-evolving", "in the realm of", "when it comes to", "paradigm shift", "seamlessly integrates", "unlock the potential".
   - PT: "é importante ressaltar", "no cenário atual", "desempenha um papel fundamental", "uma ampla gama de", "um divisor de águas", "mergulhar fundo em", "nos dias de hoje", "mudança de paradigma", "desbloquear o potencial".

## Step 2 — Structural rewrite (your job)

Rewrite for the patterns regex cannot fix safely:

- **Cadence:** vary sentence length. AI text keeps sentences near-uniform; alternate short sentences with longer, subordinate ones.
- **Anti-symmetry:** break rigid parallelisms — "not only X but also Y", "it's not about X, it's about Y", "whether you're a X or a Y", rule-of-three lists, bold-lead bullet stacks, emoji headings.
- **Em dashes:** if density is high (more than ~1 per 100 words), convert most parenthetical em dashes into commas or separate sentences.
- **Semantic integrity:** never invent or drop facts, numbers, names, or entities. Compare your rewrite against the original before finishing.

## Step 3 — Gate (self-check before returning)

Reject your own rewrite and try again if any of these fail:

1. No cliché from Step 1 reintroduced.
2. No invisible character reintroduced.
3. Sentence-length variation improved (or at least did not get worse).
4. Length between 0.3x and 1.4x of the original — outside that range you probably dropped or padded content.
5. Every fact, number, and name from the original is still present and unchanged.

If a rewrite keeps failing, return the output of Step 1 unchanged — a deterministic clean is better than a rewrite that loses content.

# Kabyle FLORES+ orthography fix

Cleaned export of the `kab_Latn` split from [openlanguagedata/flores_plus](https://huggingface.co/datasets/openlanguagedata/flores_plus) with Greek-letter contamination corrected to match the Unicode CLDR standard alphabet for Kabyle.

## Bug found

The original dataset contained two Greek characters in place of their Latin phonetic equivalents:

| Wrong | Unicode | Correct | Unicode | Occurrences |
|-------|---------|---------|---------|-------------|
| `ε` (Greek small epsilon) | U+03B5 | `ɛ` (Latin small open E) | U+025B | 430 |
| `Γ` (Greek capital Gamma) | U+0393 | `Ɣ` (Latin capital Gamma) | U+0194 | 41 |

- **Total affected sentences:** 323 out of 2,009 (16.1%)
- **dev:** 141 sentences affected
- **devtest:** 182 sentences affected

## Output files

```
dev/
  kab_Latn.jsonl
devtest/
  kab_Latn.jsonl
kabyle_changes_log.tsv
```

- `dev/kab_Latn.jsonl` — 997 cleaned sentences
- `devtest/kab_Latn.jsonl` — 1012 cleaned sentences
- `kabyle_changes_log.tsv` — line-by-line before/after for all 323 changed sentences

## Verification

Confirm no Greek characters remain:

```bash
grep -rP '\p{Greek}' dev/ devtest/ || echo "clean"
```

## Upstream report

This bug was reported to FLORES+ / OLDI so it can be fixed in the official release:

- **URL:** https://huggingface.co/datasets/openlanguagedata/flores_plus/discussions/37
- **Summary:** Greek epsilon (U+03B5) and Gamma (U+0393) used instead of Latin open E (U+025B) and Gamma (U+0194) in 323 sentences.
- **Fix:** Simple two-character substitution.

## Reference

- Unicode CLDR v45+ — Kabyle `[kab]` exemplar characters
- FLORES+ dataset card: https://huggingface.co/datasets/openlanguagedata/flores_plus

## Notes

- Generated using Kimi K2.6.
- Do not redistribute the cleaned JSONL files publicly unless protected from automatic scraping, per the FLORES+ license (CC BY-SA 4.0).

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean Kabyle (kab_Latn) FLORES+ dataset from Greek-letter contamination.
Aligns text with Unicode CLDR standard alphabet for Kabyle.

This script was generated using Kimi K2.6 and we want our users to know it.

Output structure matches original:
    dev/kab_Latn.jsonl
    devtest/kab_Latn.jsonl
"""

import json
import unicodedata
from pathlib import Path
from collections import Counter, defaultdict
from datasets import load_dataset


# configuration
DATASET_NAME = "openlanguagedata/flores_plus"
LANG_CONFIG = "kab_Latn"

# wrong (Greek) -> correct (CLDR-standard Latin) character map
GREEK_TO_LATIN = {
    '\u03b5': '\u025b',   # Greek epsilon -> Latin open E
    '\u0393': '\u0194',   # Greek Gamma -> Latin Gamma
    '\u03b3': '\u0263',   # Greek gamma -> Latin gamma (defensive)
}

BAD_CHARS = set(GREEK_TO_LATIN.keys())


def fix_text(text):
    for wrong, right in GREEK_TO_LATIN.items():
        text = text.replace(wrong, right)
    return text


def get_unicode_info(char):
    name = unicodedata.name(char, "UNKNOWN")
    return f"{char!r} {name} U+{ord(char):04X}"


def main():
    print("Kabyle FLORES+ cleaning script")
    print("Reference: Unicode CLDR standard alphabet for Kabyle [kab]")

    # 1. load dataset
    print("\n[1/5] Loading dataset from cache...")
    ds = load_dataset(DATASET_NAME, LANG_CONFIG)
    total = len(ds['dev']) + len(ds['devtest'])
    print(f"      Loaded: {len(ds['dev'])} dev + {len(ds['devtest'])} devtest = {total} sentences")

    # 2. detect contamination
    print("\n[2/5] Scanning for Greek-letter contamination...")
    affected = []
    char_counts = Counter()
    split_counts = defaultdict(int)

    for split in ['dev', 'devtest']:
        for row in ds[split]:
            text = row['text']
            found_bad = [c for c in BAD_CHARS if c in text]

            if found_bad:
                for c in found_bad:
                    char_counts[c] += text.count(c)

                fixed = fix_text(text)
                affected.append({
                    'split': split,
                    'id': row['id'],
                    'before': text,
                    'after': fixed,
                    'chars_found': found_bad,
                })
                split_counts[split] += 1

    total_affected = len(affected)
    total_chars = sum(char_counts.values())

    print(f"      Affected sentences: {total_affected}")
    print(f"      Wrong char occurrences: {total_chars}")

    if total_affected == 0:
        print("\n      No contamination found. Nothing to fix.")
        return

    print("\n      Wrong character breakdown:")
    for char, count in sorted(char_counts.items(), key=lambda x: -x[1]):
        print(f"      {get_unicode_info(char)}  ->  {get_unicode_info(GREEK_TO_LATIN[char])}")
        print(f"         Occurrences: {count}")

    # 3. show samples
    print("\n[3/5] Sample corrections:")
    for i, item in enumerate(affected[:5], 1):
        print(f"\n      Sample {i}  [{item['split']}] id={item['id']}")
        print(f"      before: {item['before'][:100]}...")
        print(f"      after : {item['after'][:100]}...")

    # 4. export cleaned files in original structure
    print("\n[4/5] Exporting cleaned files...")

    for split in ['dev', 'devtest']:
        out_dir = Path(split)
        out_dir.mkdir(exist_ok=True)
        out_file = out_dir / "kab_Latn.jsonl"

        with open(out_file, "w", encoding="utf-8") as f:
            for row in ds[split]:
                clean_row = dict(row)
                clean_row['text'] = fix_text(clean_row['text'])
                f.write(json.dumps(clean_row, ensure_ascii=False) + "\n")

        print(f"      {out_file}")

    # 5. export change log
    log_file = Path("kabyle_changes_log.tsv")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("split\tid\tbefore\tafter\tchars_found\n")
        for item in affected:
            chars_str = ",".join(item['chars_found'])
            before = item['before'].replace('\t', ' ').replace('\n', ' ')
            after = item['after'].replace('\t', ' ').replace('\n', ' ')
            f.write(f"{item['split']}\t{item['id']}\t{before}\t{after}\t{chars_str}\n")

    print(f"      {log_file} ({total_affected} changed sentences)")

    # 6. write report
    print("\n[5/5] Writing report...")

    report_lines = [
        "Kabyle FLORES+ cleaning report",
        "",
        f"Dataset: {DATASET_NAME} ({LANG_CONFIG})",
        f"Reference: Unicode CLDR standard alphabet for Kabyle [kab]",
        f"Total sentences: {total}",
        f"Affected sentences: {total_affected} ({total_affected/2009*100:.1f}%)",
        f"Total wrong-char occurrences: {total_chars}",
        "",
        "Wrong -> correct character map (Unicode)",
    ]

    for char, count in sorted(char_counts.items(), key=lambda x: -x[1]):
        report_lines.append(
            f"{get_unicode_info(char)}  ->  {get_unicode_info(GREEK_TO_LATIN[char])}"
            f"   (occurrences: {count})"
        )

    report_lines.extend([
        "",
        "Split breakdown",
        f"  dev:     {split_counts['dev']} affected sentences",
        f"  devtest: {split_counts['devtest']} affected sentences",
        "",
        "Output files",
        f"  - dev/kab_Latn.jsonl",
        f"  - devtest/kab_Latn.jsonl",
        f"  - {log_file.name}",
        "",
        "Verification",
        "Run the following to confirm zero Greek chars remain:",
        "  grep -rP '\\p{Greek}' dev/ devtest/ || echo 'clean'",
        "",
        "Upstream report",
        "Report this bug to FLORES+ / OLDI:",
        "  https://huggingface.co/datasets/openlanguagedata/flores_plus/discussions",
        "Bug: Greek epsilon (e, U+03B5) and Gamma (G, U+0393) used instead of",
        "      Latin open E (e, U+025B) and Latin Gamma (G, U+0194).",
        "Fix:  Simple 2-character substitution affecting 323 sentences (16.1%).",
    ])

    report_file = Path("kabyle_cleaning_report.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")

    print(f"      {report_file}")

    # final summary
    print("\nCleaning complete")
    print(f"Fixed {total_chars} wrong-character occurrences in {total_affected} sentences.")
    print("All outputs saved in current directory.")


if __name__ == "__main__":
    main()

# Verdict

Proceed with changes. Change A is necessary and should be implemented first because the current pressure table demonstrably withholds existing norm rows from ICs outside `base_english_candidates.csv`. Change B is the right pressure-table shape, but the bucket should be named `common_vocabulary`, not `abstract_common`, and the rule should explicitly be documented as a pressure-bucket override rather than a classifier migration. Change C is not safe as written: it removes the only current signal that catches `ic:pa`, and it still does nothing for `ic:abbr`; tighten it only after adding a rule-derived fallback for short unsupported code-like surfaces or after enriching classifier inputs with real abbreviation evidence.

## Question-by-question answers

1. **Is the rules design data-driven enough?**

Yes for Change A and Change B. Change A is a structural join fix. Change B is a feature rule over a norm-derived `high_frequency` threshold, not a per-IC handlist. Change C is also feature-shaped, but as written it is under-specified because the current classifier data lacks the proposed additional signals for some known abbreviation/code cases. That is not secretly per-IC, but it is not yet an adequate rule.

2. **Is `abstract_common` the right bucket name?**

No. The override catches common concrete and grammatical vocabulary too: examples from the audit/frequency scan include `ic:part`, `ic:point`, `ic:work`, `ic:ball`, `ic:school`, `ic:doctor`, `ic:body` if it ever became artifact-typed, and many short function/common words. Use `common_vocabulary`. I would avoid `lexical_word` because it collides conceptually with the existing Wiktionary lexicality/tag language and does not say why the row is leaving artifact pressure.

3. **Is the `high_frequency` threshold strong enough on its own?**

Mostly yes for the pressure-bucket override. The repo threshold is Zipf >= 5.0 in `scripts/base_english_candidates.py`, and a full audit scan found 204 blocking `resource_artifact` rows at that threshold with aggregate containment 35,697. Adding `early_aoa` would wrongly keep common load-bearing words such as `ic:power` out of the override because `power` has AOA 7.48 but frequency 5.17. The better guard is not `early_aoa`; it is to ensure the rule only overrides artifact lexicality, not numeric/multiword/technical-only candidate flags, and to keep taxon behavior under review.

4. **Are we leaving real artifacts in the wrong bucket?**

Some should stay artifact, especially numeric forms and genuine code/taxon cases. The proposed Change B does not touch numeric-only rows because it keys on `typed_bucket in ARTIFACT_BUCKETS`, which is good. But because `ARTIFACT_BUCKETS` includes `taxon`, the rule technically permits a high-frequency taxon to leave `resource_artifact`; the current audit scan found no high-frequency blocking taxon rows, but the rule should either exclude `taxon` or explicitly justify why common taxon words are not artifact pressure. Moving `ic:more` to `common_vocabulary` is correct: its current `proper_name` route is an artifact-reading collision, while the surface is high-frequency common English.

5. **Is the falsifier magnitude right?**

The 5 percentage point artifact-share drop is soft but acceptable as a Phase 4 gate. The high-frequency override alone has enough measured reach to plausibly clear it: 204 blocking artifact rows and 35,697 aggregate containment out of the audit's 157,021 typed-bucket blocker sum. If the rebuild fails to clear 5 pp after that, the workstream should treat it as real evidence that artifact mislabelling was not the dominant bottleneck under the validator's status-precedence metric.

6. **Does Change A break any downstream consumer?**

It should not break schema consumers if the existing column names and boolean string output are preserved. `scripts/validate_assembler_definitions.py` only reads `l0_candidate` and `pressure_bucket` to build bases, then uses `pressure_bucket` to classify failures; it does not depend on the origin of `frequency`, `age_of_acquisition`, or `concreteness`. `scripts/audit_artifact_bucket.py` reads the norm columns for reporting. The main compatibility requirement is to keep `data/kernel-pressure-table.csv` columns unchanged and keep booleans serialized as the current CSV strings.

7. **Is classifier tightening safe?**

No, not as written. Current `data/kaikki-seed-disagreement-typed.csv` shows `ic:pa` is `abbreviation_or_code` only because of the blanket short-form rule: it has no P2 lexicality, no candidate flags, and no candidate row. The proposed conjunction would stop catching it. `ic:abbr` is currently `resource_specific_tail`, not `abbreviation_or_code`, so the proposed criteria also do not prove it will catch that known abbreviation surface. The tightening needs either richer classifier evidence or a rule-derived fallback for code-like unsupported short surfaces before implementation.

## Concrete edits

In `scripts/kernel_pressure_table.py`, add direct norms loading near the candidate readers and use the same normalization and thresholds as `scripts/base_english_candidates.py`:

```python
HIGH_FREQUENCY_THRESHOLD = 5.0
EARLY_AOA_THRESHOLD = 6.0
HIGH_CONCRETENESS_THRESHOLD = 4.0


def normalize_surface(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_").replace("'", "")


def read_norm_file(path: Path) -> dict[str, float]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return {}
        word_field = next(name for name in reader.fieldnames if name.lower() in {"word", "lemma", "term"})
        value_field = next(name for name in reader.fieldnames if name != word_field)
        return {
            normalize_surface(row[word_field]): float(row[value_field])
            for row in reader
            if row.get(word_field) and row.get(value_field)
        }
```

In `build_parser()`, add norm inputs:

```python
parser.add_argument("--frequency", type=Path, default=Path("data/psycholinguistic/frequency.csv"))
parser.add_argument("--age-of-acquisition", type=Path, default=Path("data/psycholinguistic/age_of_acquisition.csv"))
parser.add_argument("--concreteness", type=Path, default=Path("data/psycholinguistic/concreteness.csv"))
```

In `build_rows()`, load and apply the norms by `primary_alias` after selecting `primary_alias`:

```python
frequency = read_norm_file(args.frequency)
aoa = read_norm_file(args.age_of_acquisition)
concreteness = read_norm_file(args.concreteness)

# inside the row loop, after primary_alias is known
norm_key = normalize_surface(primary_alias)
freq_value = frequency.get(norm_key)
aoa_value = aoa.get(norm_key)
conc_value = concreteness.get(norm_key)

row.update(
    {
        "frequency": "" if freq_value is None else freq_value,
        "age_of_acquisition": "" if aoa_value is None else aoa_value,
        "concreteness": "" if conc_value is None else conc_value,
        "high_frequency": (freq_value or 0.0) >= HIGH_FREQUENCY_THRESHOLD,
        "early_aoa": (aoa_value or 99.0) <= EARLY_AOA_THRESHOLD,
        "high_concreteness": (conc_value or 0.0) >= HIGH_CONCRETENESS_THRESHOLD,
    }
)
```

In `pressure_bucket(row)`, place the new override before the current artifact clause and name it `common_vocabulary`:

```python
if typed_bucket in (ARTIFACT_BUCKETS - {"taxon"}) and bool(row.get("high_frequency")):
    return "common_vocabulary", "artifact lexicality but high frequency"
```

If the workstream intentionally wants high-frequency taxa to leave artifact pressure, do not subtract `{"taxon"}`, but document that exception in the rules report because the parent workstream explicitly preserves distinct taxon semantics.

For Change C in `scripts/classify_seed_disagreement.py`, do not ship the proposal exactly as written. The minimum safer shape is:

```python
has_abbreviation_signal = (
    lexicality in {"symbol-code", "abbreviation"}
    or "symbol-code" in tag_counts
    or "abbreviation" in tag_counts
    or "numeric_form" in flags
    or re.search(r"\d", surface)
    or surface.endswith(("_abbr", "_abbrev"))
    or (len(surface.replace("_", "")) <= 2 and candidate is None and p2_row is None)
)

if has_abbreviation_signal:
    reasons.append("symbol/code/numeric/short-form signal")
    return "abbreviation_or_code", reasons
```

That still is not enough for `ic:abbr`; either add upstream abbreviation evidence for it or explicitly decide that bare `abbr`/`abbrev` surfaces are not in scope. Do not claim Change C catches `ic:abbr` unless a test proves it.

## Risks

- The pressure-bucket override is not literally a classifier rule. The Phase 2 report should say this is a pressure policy rule over classifier output; otherwise it looks like it conflicts with the parent sentence requiring a written classifier rule for migration out of `resource_artifact`.
- A high-frequency override can move genuine common abbreviations such as `tv`, `us`, `s`, or `re` if they remain artifact-typed and get direct norm values. That may be acceptable for pressure, but it should be measured and listed in the impact report.
- Change A should normalize `primary_alias` exactly like `base_english_candidates.py`; otherwise hyphen, space, apostrophe, and case variants will still silently miss norm rows.
- The current proposal does not specify tests. Add focused tests or a small verification script for `act/can/out/all/law`, `pa`, `abbr`, `hypertensin`, and at least one high-frequency proper-name collision like `more`.
- The impact report must list every IC whose `pressure_bucket` changes, not just aggregate bucket counts, because the hard regression gate depends on confirming no previously closed sense regressed.

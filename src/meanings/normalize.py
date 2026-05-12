from __future__ import annotations

import re

TOKEN_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")

# Gloss parsing needs a stronger blocklist than ordinary tokenization because
# dictionary definitions reuse a small amount of editorial glue at very high
# frequency. If we keep these lemmas, they dominate the kernel and swamp the
# more semantically interesting structure.
FUNCTION_WORDS = {
    "a",
    "an",
    "and",
    "any",
    "anybody",
    "anyone",
    "anything",
    "are",
    "as",
    "at",
    "become",
    "be",
    "being",
    "between",
    "but",
    "by",
    "each",
    "either",
    "every",
    "for",
    "from",
    "have",
    "having",
    "he",
    "her",
    "hers",
    "him",
    "his",
    "i",
    "in",
    "into",
    "is",
    "it",
    "its",
    "itself",
    "me",
    "my",
    "neither",
    "not",
    "of",
    "on",
    "one",
    "ones",
    "only",
    "or",
    "other",
    "our",
    "ours",
    "own",
    "same",
    "she",
    "some",
    "somebody",
    "someone",
    "something",
    "such",
    "that",
    "the",
    "their",
    "them",
    "themselves",
    "there",
    "these",
    "this",
    "those",
    "to",
    "we",
    "what",
    "when",
    "where",
    "which",
    "who",
    "whom",
    "whose",
    "with",
    "you",
    "your",
    "yours",
}

GLOSS_GLUE = {
    "another",
    "especially",
    "including",
    "kind",
    "made",
    "mainly",
    "manner",
    "often",
    "particular",
    "relating",
    "respectively",
    "similar",
    "sometimes",
    "sort",
    "typically",
    "used",
    "use",
    "using",
    "usually",
}

TAXONOMIC_GLUE = {
    "action",
    "class",
    "family",
    "genus",
    "grouping",
    "kind",
    "member",
    "members",
    "order",
    "person",
    "people",
    "process",
    "species",
    "state",
    "subspecies",
    "type",
    "way",
}

NUMBER_WORDS = {
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
}

STOPWORDS = FUNCTION_WORDS | GLOSS_GLUE | TAXONOMIC_GLUE | NUMBER_WORDS


def normalize_lemma(text: str) -> str:
    text = text.strip().lower().replace("-", "_").replace(" ", "_")
    text = text.replace("'", "")
    return text


def basic_tokens(text: str) -> list[str]:
    return [match.group(0).lower().replace("'", "") for match in TOKEN_RE.finditer(text)]


def content_tokens(text: str) -> list[str]:
    return [token for token in basic_tokens(text) if token not in STOPWORDS]


def is_titlecase_span(raw_tokens: list[str]) -> bool:
    return bool(raw_tokens) and all(token[:1].isupper() for token in raw_tokens)


def extract_lemma_candidates(text: str, lemma_set: set[str], max_n: int = 3) -> list[str]:
    token_pairs = [
        (match.group(0), match.group(0).lower().replace("'", ""))
        for match in TOKEN_RE.finditer(text)
    ]
    filtered_pairs = [(raw, token) for raw, token in token_pairs if token not in STOPWORDS]
    raw_tokens = [raw for raw, _ in filtered_pairs]
    tokens = [token for _, token in filtered_pairs]
    matches: list[str] = []
    index = 0
    while index < len(tokens):
        titlecase_width = 0
        for width in range(max_n, 1, -1):
            if index + width > len(tokens):
                continue
            if is_titlecase_span(raw_tokens[index : index + width]):
                titlecase_width = width
                break
        if titlecase_width:
            index += titlecase_width
            continue

        matched = False
        for width in range(max_n, 0, -1):
            if index + width > len(tokens):
                continue
            candidate = "_".join(tokens[index : index + width])
            if candidate in lemma_set:
                matches.append(candidate)
                index += width
                matched = True
                break
        if not matched:
            index += 1
    return matches

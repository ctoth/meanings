from __future__ import annotations

import json

import wn


def compact_dir(obj: object) -> list[str]:
    names = []
    for name in dir(obj):
        if name.startswith("_"):
            continue
        value = getattr(obj, name)
        if callable(value):
            names.append(f"{name}()")
        else:
            names.append(name)
    return sorted(names)


def main() -> None:
    wn.download("oewn:2024")
    lex = wn.Wordnet("oewn:2024")
    synset = lex.synsets("coffee")[0]
    word = lex.words("coffee")[0]
    sense = word.senses()[0]
    payload = {
        "lexicon": str(lex),
        "synset_id": synset.id,
        "synset_dir": compact_dir(synset),
        "word_id": word.id,
        "word_dir": compact_dir(word),
        "sense_id": sense.id,
        "sense_dir": compact_dir(sense),
        "sense_synset_id": sense.synset().id,
        "sense_pos": sense.synset().pos,
        "synset_definition": synset.definition(),
        "synset_lemmas": [w.lemma() for w in synset.words()],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()

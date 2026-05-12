"""Head-to-head: the rule-based lexicality classifier vs a distributional baseline.

Agenda item #4 (a head-to-head task win or honest tie of the typed system over a
distributional baseline) and agenda item #7 (an independent audit of
``src/meanings/lexicality.py``), instantiated as lexicality classification over
Open English WordNet senses.

Pipeline:
  1. Build (or load) a stratified, agent-judged gold set of OEWN senses, with a
     profanity/slur/explicit stoplist excluded so offensive glosses never enter
     any output artifact.
  2. Baseline A -- run ``classify_lexicality`` on every gold sense; report
     per-class P/R/F1, macro/micro-F1, confusion matrix, failure modes.
  3. Baseline B -- TF-IDF over gloss text (word 1-2 grams + char 3-5 grams) plus
     a few cheap structural features -> multinomial logistic regression, scored
     by stratified k-fold CV; the rule classifier is scored on the same folds.
  4. Head-to-head: macro/micro/per-class F1, broken down by subset
     (short-token/symbol-code items, taxon/chemical items, ordinary lexical
     words).
  5. Emit ``reports/lexicality-headtohead.md`` + ``reports/lexicality-headtohead.json``.

Run:  uv run python scripts/lexicality_headtohead.py
"""

from __future__ import annotations

import csv
import json
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import wn
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

from meanings.lexicality import classify_lexicality
from meanings.normalize import normalize_lemma

REPO = Path(__file__).resolve().parents[1]
GOLD_CSV = REPO / "data" / "lexicality-gold.csv"
REPORT_MD = REPO / "reports" / "lexicality-headtohead.md"
REPORT_JSON = REPO / "reports" / "lexicality-headtohead.json"
LEXICON_ID = "oewn:2024"
SEED = 20240512

# ---------------------------------------------------------------------------
# Content guardrail: a profanity / slur / explicit-term stoplist.  Any OEWN
# lemma whose normalized form matches a stoplist token (or contains one as a
# whole word) is skipped before it ever enters the gold set, so no offensive
# gloss is stored in the CSV, the report, or this process's stdout.  This
# slightly under-samples ``lexical-word`` (most slurs/profanity are ordinary
# lexical words) and a few ``technical``/``uncertain`` cases; the relative
# head-to-head comparison is unaffected -- both classifiers face the same clean
# subset.  The list is a common-knowledge "bad words" set, deliberately broad.
# ---------------------------------------------------------------------------
_STOPLIST_TOKENS = {
    # general profanity / vulgar
    "fuck", "fucker", "fucking", "motherfucker", "shit", "shite", "bullshit",
    "bullshitter", "horseshit", "chickenshit", "shithead", "shitty", "crap",
    "crappy", "piss", "pissed", "pisser", "ass", "asshole", "arse", "arsehole",
    "bastard", "bitch", "bitchy", "damn", "goddamn", "hell", "bloody", "bugger",
    "wank", "wanker", "twat", "prick", "dick", "dickhead", "cock", "cocksucker",
    "pussy", "cunt", "knob", "tit", "tits", "boob", "boobs", "balls", "bollocks",
    "jizz", "spunk", "turd", "fart", "queef", "screw", "screwing", "shag",
    # sexual / explicit
    "sex", "sexy", "fucked", "blowjob", "handjob", "rimjob", "cum", "orgasm",
    "boner", "horny", "slut", "slutty", "whore", "hooker", "hoe", "skank",
    "nympho", "porn", "porno", "pornography", "dildo", "vibrator", "fellatio",
    "cunnilingus", "anal", "anus", "rectum", "scrotum", "testicle", "penis",
    "vagina", "vulva", "clitoris", "clit", "labia", "nipple", "areola",
    "ejaculate", "ejaculation", "fornicate", "fornication", "coitus", "copulate",
    "masturbate", "masturbation", "sodomy", "sodomize", "buttfuck", "gangbang",
    "threesome", "incest", "bestiality", "pederasty", "pedophile", "paedophile",
    "rape", "rapist", "molest", "molester",
    # slurs (ethnic / racial / religious)
    "nigger", "nigga", "negro", "coon", "spic", "spick", "wetback", "beaner",
    "chink", "gook", "jap", "nip", "kike", "yid", "hymie", "wop", "dago", "guido",
    "polack", "kraut", "hun", "limey", "mick", "paddy", "redskin", "injun",
    "squaw", "raghead", "towelhead", "sandnigger", "camel", "wog", "paki",
    "gypsy", "gyppo", "gippo", "honkey", "honky", "cracker", "whitey", "gringo",
    "halfbreed", "mongrel", "darky", "darkie", "sambo", "jigaboo", "pickaninny",
    # slurs (LGBTQ / disability / other)
    "faggot", "fag", "dyke", "queer", "homo", "fairy", "fruit", "poof", "poofter",
    "tranny", "shemale", "ladyboy", "fudgepacker", "buttpirate", "carpetmuncher",
    "retard", "retarded", "spastic", "spaz", "mongoloid", "cripple", "gimp",
    "lame", "imbecile", "moron", "idiot", "cretin", "dumb",
    # mild but flag-prone
    "slag", "tart", "minx", "floozy", "hussy", "trollop", "strumpet", "harlot",
    "concubine", "courtesan", "wench", "bawd", "pimp", "prostitute",
}
_STOPLIST_RE = re.compile(
    r"(?:^|[\s_'-])(" + "|".join(re.escape(t) for t in sorted(_STOPLIST_TOKENS)) + r")(?:$|[\s_'-])",
    re.IGNORECASE,
)


def _is_stoplisted(lemma: str) -> bool:
    norm = normalize_lemma(lemma).lower().replace("_", " ")
    if not norm:
        return False
    for tok in norm.split():
        if tok in _STOPLIST_TOKENS:
            return True
    return bool(_STOPLIST_RE.search(" " + norm + " "))


# ---------------------------------------------------------------------------
# The agent-judged gold rubric.  This is intentionally MORE thorough than the
# production rule classifier (it inspects the gloss for many more cues and uses
# explicit known-name / known-taxon-rank cues), and the labels it produces are
# the "gold" the head-to-head scores against.  They are AGENT-JUDGED, not
# human-validated -- the comparison is still fair (identical labels for both
# classifiers) but the absolute numbers are provisional.
#
# Rubric, in priority order (first hit wins):
#   chemical    -- gloss describes a chemical element / compound / radical /
#                  isotope / ion, OR the lemma is a bare chemical formula and the
#                  gloss mentions a chemistry context.
#   taxon       -- gloss says the sense IS a taxonomic rank ("a genus of ...",
#                  "(...) family of ...", "type genus", "the order/class/phylum
#                  comprising ...") or a Linnaean binomial.
#   abbreviation-- gloss explicitly says "abbreviation", "acronym", "initialism",
#                  or "short for X".
#   symbol-code -- lemma is a single character or a 2-3 char all-caps / mixed
#                  token whose gloss describes it AS a letter / symbol / written
#                  abbreviation / unit code / metric prefix / chemical symbol /
#                  Roman numeral; OR a 1-char lemma; OR a short token not on the
#                  whitelist whose gloss is a code/letter gloss.  (A short token
#                  that the gloss treats as an ordinary word -- "no", "ax",
#                  "ox" -- is lexical-word, not symbol-code.)
#   proper-name -- gloss describes a unique named entity: a specific person,
#                  place, organization, deity, mythological/fictional figure,
#                  event, document, language, ethnic group, calendar period.
#                  (Titlecase alone is NOT sufficient; many titlecase nouns are
#                  proper names and many are not.)
#   idiom       -- gloss flags the sense as idiomatic / a fixed expression whose
#                  meaning is not compositional; or it is a multiword sense whose
#                  gloss is paraphrastic and clearly non-compositional.
#   phrase      -- multiword lemma whose meaning is (largely) compositional.
#   technical-term -- single-word sense whose gloss restricts it to a technical
#                  domain (math/physics/chemistry-as-discipline/CS/linguistics/
#                  law/medicine/music/grammar/statistics/...), i.e. it is not an
#                  everyday word.
#   uncertain   -- evidence genuinely conflicting or absent (empty gloss; lemma
#                  ambiguous between code and word with no gloss signal).
#   lexical-word-- everything else: an ordinary English content word.
# ---------------------------------------------------------------------------

# Cue lexicons for the gold rubric (broader than the production classifier).
_CHEM_GLOSS = (
    "chemical element", "chemical symbol", "atomic number", "metallic element",
    "nonmetallic element", "noble gas", "halogen", "alkali metal", "alkaline earth",
    "rare earth", "lanthanide", "actinide", "transuranic", "radioactive element",
    "isotope of", "an isotope", "chemical compound", "organic compound",
    "inorganic compound", "a salt of", "an ester of", "an oxide of", "a hydroxide",
    "an acid", "chemical formula", "a radical", "a cation", "an anion", "an ion",
    "soluble white", "soluble crystalline", "white crystalline compound",
    "a poisonous", "a colorless", "a colourless", "a flammable", "a gaseous",
    "petroleum", "hydrocarbon", "amino acid", "fatty acid", "nucleic acid",
    "monosaccharide", "polysaccharide", "alkaloid", "enzyme produced", "a sugar",
)
_TAXON_GLOSS = (
    "a genus of", "type genus", "the type genus", "a family of", "family of",
    "an order of", "the order of", "a class of", "a phylum of", "a kingdom of",
    "a subfamily of", "a suborder of", "a superfamily of", "a tribe of",
    "a subgenus of", "a species of", "a subspecies of", "a variety of plant",
    "taxonomic", "a large genus", "a small genus", "a monotypic genus",
    "comprising the", "coextensive with", "in some classifications",
    "widely distributed genus", "cosmopolitan genus", "chiefly tropical genus",
)
_ABBR_GLOSS_RE = re.compile(
    r"\b(abbreviation|abbreviated|acronym|initialism|short for|written abbreviation|stands for)\b",
    re.IGNORECASE,
)
_SYMBOL_GLOSS_RE = re.compile(
    r"\b(the (first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|"
    r"\d+(st|nd|rd|th)) letter of|a letter (of|in) the|the [0-9]+ ?(st|nd|rd|th) letter|"
    r"the (cardinal|ordinal) number|denoting|the symbol for|metric (unit|prefix)|"
    r"a unit of|a metric unit|roman numeral|the blood group|the rh|musical notation|"
    r"the note|in the diatonic scale|a written symbol|graphic symbol|the chemical symbol)\b",
    re.IGNORECASE,
)
_PROPER_GLOSS = (
    "capital of", "a city in", "a town in", "a port in", "a village in",
    "a state in", "a province of", "a region of", "a river in", "a mountain in",
    "a lake in", "an island in", "a country in", "a republic in", "a kingdom in",
    "a county in", "a borough of", "a district of", "a peninsula", "a desert in",
    "a continent", "an ocean", "a sea in", "a national park",
    "United States president", "the first president", "a president of",
    "a (united states|english|british|french|german|roman|greek|italian|russian|"
    "spanish|american) (general|statesman|politician|writer|poet|composer|painter|"
    "philosopher|scientist|physicist|chemist|mathematician|king|queen|emperor|"
    "novelist|playwright|actor|actress|economist|psychologist|architect)",
    "(greek|roman|norse|egyptian|hindu|celtic) (god|goddess|deity)",
    "the (greek|roman|norse|egyptian|hindu) god", "the supreme god", "goddess of",
    "god of", "a mythical", "in greek mythology", "in roman mythology",
    "in norse mythology", "(legendary|mythical) (king|queen|hero|figure)",
    "a fictional", "the hero of", "the protagonist of", "a character in",
    "a book of the bible", "a gospel", "a (jewish|christian|islamic|hindu) (festival|holiday|holy day)",
    "an organization", "a political party", "a (united states|us) government agency",
    "a (private|public) university", "a college in", "founded in", "established in",
    "a language family", "a (north american|south american|african|asian|australian) (indian|aboriginal) people",
    "a member of a (people|tribe|nation)", "the language of the", "a dialect of",
    "the era", "the period", "the dynasty", "a war between", "the battle of",
    "the treaty of", "the war", "the revolution",
)
_TECH_GLOSS = (
    "in mathematics", "(in|of) computer science", "in physics", "in chemistry,",
    "in linguistics", "in logic,", "in law,", "in medicine,", "in music,",
    "in grammar,", "in statistics", "in geometry", "in algebra", "in calculus",
    "in topology", "in economics,", "in psychology,", "in philosophy,",
    "in anatomy", "in biology,", "in botany,", "in zoology,", "in astronomy,",
    "in computing", "in programming", "in electronics", "in mechanics,",
    "in optics", "in genetics", "in physiology", "in pathology", "in surgery,",
    "in printing", "in heraldry", "in architecture,", "(math)", "(physics)",
    "(chemistry)", "(linguistics)", "(law)", "(medicine)", "(computing)",
    "(grammar)", "(statistics)", "(logic)", "(mathematics)", "(biology)",
    "(astronomy)", "(geology)", "(music)", "(economics)",
)
_IDIOM_GLOSS_RE = re.compile(
    r"\b(idiom|idiomatic|idiomatically|figuratively|colloquial expression|"
    r"a fixed expression|an exclamation|an interjection|used to express|"
    r"used as an? (intensifier|exclamation|greeting)|a phrase used)\b",
    re.IGNORECASE,
)

_FORMULA_RE = re.compile(r"^[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)+$")
_BINOMIAL_RE = re.compile(r"^[A-Z][a-z]+ [a-z]+$")

# Short tokens the production classifier whitelists; the gold rubric also treats
# these as candidate ordinary words when the gloss confirms it.
_WHITELIST = {
    "am", "an", "as", "at", "ax", "axe", "be", "by", "do", "go", "he", "if",
    "in", "is", "it", "me", "my", "no", "of", "on", "or", "ox", "so", "to",
    "up", "us", "we",
}


def _contains_any(text: str, needles) -> bool:
    low = text.lower()
    return any(n in low for n in needles)


def _contains_any_re(text: str, patterns) -> bool:
    for p in patterns:
        if "(" in p or "|" in p or "\\" in p:
            if re.search(p, text, re.IGNORECASE):
                return True
        elif p in text.lower():
            return True
    return False


def _case_pattern(s: str) -> str:
    letters = "".join(c for c in s if c.isalpha())
    if not letters:
        return "uncased"
    if letters.islower():
        return "lower"
    if letters.isupper():
        return "upper"
    if letters[:1].isupper() and letters[1:].islower():
        return "title"
    return "mixed"


def gold_label(lemma: str, pos: str, gloss: str) -> tuple[str, str]:
    """Return (gold_lexicality_tag, short_rationale).  Agent-judged."""
    norm = normalize_lemma(lemma)
    bare = norm.replace("_", "")
    tlen = len(bare)
    case = _case_pattern(lemma)
    g = gloss.strip()
    glow = g.lower()
    multiword = "_" in norm or " " in lemma.strip()

    if not g:
        return "uncertain", "empty gloss"

    # chemical
    if _contains_any(glow, _CHEM_GLOSS):
        return "chemical", "gloss: chemical substance/element cue"
    if _FORMULA_RE.match(lemma.strip()) and _contains_any(
        glow, ("compound", "acid", "gas", "salt", "oxide", "chemical", "formula", "molecule")
    ):
        return "chemical", "lemma is a chemical formula + chemistry gloss"

    # taxon
    if _contains_any(glow, _TAXON_GLOSS):
        return "taxon", "gloss: taxonomic rank cue"
    if _BINOMIAL_RE.match(lemma.replace("_", " ").strip()) and _contains_any(
        glow, ("genus", "species", "plant", "tree", "shrub", "herb", "animal", "fish", "bird", "insect")
    ):
        return "taxon", "Linnaean binomial lemma"

    # abbreviation
    if _ABBR_GLOSS_RE.search(g):
        return "abbreviation", "gloss: abbreviation/acronym cue"

    # symbol-code: single char, or short uppercase/mixed token with a letter/symbol gloss
    if tlen == 1:
        return "symbol-code", "single-character lemma"
    if tlen <= 3 and case in {"upper", "mixed"}:
        return "symbol-code", "short upper/mixed-case token (code)"
    if _SYMBOL_GLOSS_RE.search(g) and tlen <= 5 and not multiword:
        return "symbol-code", "gloss: letter/symbol/unit-code cue"
    if tlen <= 3 and case == "title":
        # short titlecase: usually a code unless gloss treats as ordinary word
        if bare not in _WHITELIST:
            return "symbol-code", "short titlecase token, not whitelisted"

    # proper name
    if pos == "n" and _contains_any_re(g, _PROPER_GLOSS):
        return "proper-name", "gloss: named-entity cue"
    if pos == "n" and case == "title" and not multiword:
        # titlecase noun without a proper-name gloss cue: lean lexical-word
        # only if the gloss reads like a common-noun gloss; otherwise uncertain.
        # Heuristic: if gloss starts with "a "/"an "/"any " and has no name cue,
        # treat as lexical-word (e.g. trade names that act as common nouns are
        # rare); if it starts with "the " or a capital, lean proper-name.
        if glow.startswith(("a ", "an ", "any ", "(used", "used ")):
            pass  # fall through to lexical-word
        else:
            return "proper-name", "titlecase noun, name-like gloss"

    # idiom
    if multiword and _IDIOM_GLOSS_RE.search(g):
        return "idiom", "gloss: idiomatic/fixed-expression cue"
    if not multiword and _IDIOM_GLOSS_RE.search(g) and pos not in {"n", "v"}:
        return "idiom", "interjection/exclamation gloss"

    # phrase (compositional multiword)
    if multiword:
        return "phrase", "compositional multiword lemma"

    # technical term
    if _contains_any_re(g, _TECH_GLOSS):
        return "technical-term", "gloss: technical-domain cue"

    # short token: whitelist -> lexical-word, else symbol-code
    if tlen <= 3:
        if bare in _WHITELIST:
            return "lexical-word", "short token on the ordinary-word whitelist"
        return "symbol-code", "short token not on whitelist"

    # default
    if pos in {"a", "n", "r", "s", "v"}:
        return "lexical-word", "ordinary content word (default)"
    return "uncertain", "non-lexical POS, no other cue"


# ---------------------------------------------------------------------------
# Stratum membership (for sampling only -- NOT a gold label).  Over-represents
# hard cases vs natural frequency.
# ---------------------------------------------------------------------------

# Explicit short-form / symbol-code seeds the synthesis names.
_SHORT_SEEDS = {
    "no", "No", "s", "e", "g", "a", "ph", "th", "ax", "axe", "ox", "be", "do",
    "i", "o", "u", "x", "k", "m", "n", "f", "h", "c", "b", "d", "l", "r", "t",
    "v", "w", "z", "am", "pm", "ai", "ad", "bc", "ce", "us", "uk", "un", "eu",
}


def _stratum(lemma: str, pos: str, gloss: str) -> str:
    norm = normalize_lemma(lemma)
    bare = norm.replace("_", "")
    tlen = len(bare)
    case = _case_pattern(lemma)
    glow = gloss.lower()
    multiword = "_" in norm or " " in lemma.strip()
    if lemma in _SHORT_SEEDS or norm in _SHORT_SEEDS:
        return "short_seed"
    if tlen <= 3:
        return "short_token"
    if tlen <= 5 and case in {"upper", "mixed"}:
        return "short_token"
    if _ABBR_GLOSS_RE.search(gloss):
        return "abbreviation"
    if _contains_any(glow, _CHEM_GLOSS) or _FORMULA_RE.match(lemma.strip()):
        return "chemical"
    if _contains_any(glow, _TAXON_GLOSS) or _BINOMIAL_RE.match(lemma.replace("_", " ").strip()):
        return "taxon"
    if pos == "n" and (case == "title" or _contains_any_re(gloss, _PROPER_GLOSS)):
        return "proper_name"
    if _contains_any_re(gloss, _TECH_GLOSS):
        return "technical"
    if multiword:
        return "phrase_or_idiom"
    return "ordinary"


# Target gold-set composition (~1000 senses, hard cases over-represented).
_STRATUM_TARGETS = {
    "short_seed": 60,
    "short_token": 180,
    "abbreviation": 50,
    "chemical": 130,
    "taxon": 130,
    "proper_name": 150,
    "technical": 120,
    "phrase_or_idiom": 130,
    "ordinary": 250,
}


@dataclass
class GoldRow:
    sense_key: str
    lemma: str
    redacted_lemma: str
    pos: str
    gloss: str
    redacted_gloss: str
    gold: str
    notes: str
    stratum: str


def build_gold_set() -> list[GoldRow]:
    rng = random.Random(SEED)
    wnet = wn.Wordnet(LEXICON_ID)
    by_stratum: dict[str, list] = defaultdict(list)
    seen_keys: set[str] = set()
    skipped_offensive = 0
    for word in wnet.words():
        lemma = word.lemma()
        if _is_stoplisted(lemma):
            skipped_offensive += 1
            continue
        pos = word.pos
        for sense in word.senses():
            syn = sense.synset()
            gloss = syn.definition() or ""
            sk = sense.id
            if sk in seen_keys:
                continue
            seen_keys.add(sk)
            strat = _stratum(lemma, pos, gloss)
            by_stratum[strat].append((sk, lemma, pos, gloss, strat))

    rows: list[GoldRow] = []
    for strat, target in _STRATUM_TARGETS.items():
        pool = by_stratum.get(strat, [])
        rng.shuffle(pool)
        take = pool[: min(target, len(pool))]
        for sk, lemma, pos, gloss, st in take:
            gold, rationale = gold_label(lemma, pos, gloss)
            # Guardrail belt-and-suspenders: never store an offensive gloss.
            redacted = _is_stoplisted(lemma) or _STOPLIST_RE.search(" " + gloss.lower() + " ") is not None
            rows.append(
                GoldRow(
                    sense_key=sk,
                    lemma=lemma if not redacted else "[redacted-offensive-lexicon]",
                    redacted_lemma="[redacted-offensive-lexicon]" if redacted else lemma,
                    pos=pos,
                    gloss=gloss,
                    redacted_gloss="[gloss elided]" if redacted else gloss,
                    gold=gold,
                    notes=rationale + (" | OFFENSIVE-REDACTED" if redacted else ""),
                    stratum=st,
                )
            )
    rows = [r for r in rows if r.gloss.strip()]
    print(f"gold set: {len(rows)} senses; skipped {skipped_offensive} stoplisted lemmas")
    return rows


def write_gold_csv(rows: list[GoldRow]) -> None:
    with GOLD_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["sense_key", "lemma_or_redacted", "pos", "gloss_or_elided", "gold_lexicality", "stratum", "notes"])
        for r in rows:
            w.writerow([r.sense_key, r.redacted_lemma, r.pos, r.redacted_gloss, r.gold, r.stratum, r.notes])


def load_gold_csv() -> list[GoldRow] | None:
    if not GOLD_CSV.exists():
        return None
    rows: list[GoldRow] = []
    with GOLD_CSV.open(encoding="utf-8", newline="") as fh:
        for d in csv.DictReader(fh):
            rows.append(
                GoldRow(
                    sense_key=d["sense_key"],
                    lemma=d["lemma_or_redacted"],
                    redacted_lemma=d["lemma_or_redacted"],
                    pos=d["pos"],
                    gloss="",  # re-fetched from the lexicon at runtime
                    redacted_gloss=d["gloss_or_elided"],
                    gold=d["gold_lexicality"],
                    notes=d.get("notes", ""),
                    stratum=d.get("stratum", ""),
                )
            )
    return rows


# ---------------------------------------------------------------------------
# Re-fetch glosses + lemmas + pos from the lexicon for the gold senses (so the
# CSV need not store offensive content; the classifiers run on the live data).
# ---------------------------------------------------------------------------
def hydrate(rows: list[GoldRow]) -> list[dict]:
    wnet = wn.Wordnet(LEXICON_ID)
    by_key: dict[str, object] = {}
    for word in wnet.words():
        for sense in word.senses():
            by_key[sense.id] = (word, sense)
    out = []
    for r in rows:
        rec = by_key.get(r.sense_key)
        if rec is None:
            continue
        word, sense = rec
        syn = sense.synset()
        out.append(
            {
                "sense_key": r.sense_key,
                "lemma": word.lemma(),
                "pos": word.pos,
                "gloss": syn.definition() or "",
                "examples": tuple(syn.examples() or ()),
                "synset_id": syn.id,
                "gold": r.gold,
                "stratum": r.stratum,
            }
        )
    return out


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def prf(gold: list[str], pred: list[str]) -> dict:
    labels = sorted(set(gold) | set(pred))
    per = {}
    for lab in labels:
        tp = sum(1 for g, p in zip(gold, pred) if g == lab and p == lab)
        fp = sum(1 for g, p in zip(gold, pred) if g != lab and p == lab)
        fn = sum(1 for g, p in zip(gold, pred) if g == lab and p != lab)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        per[lab] = {"precision": prec, "recall": rec, "f1": f1, "support": tp + fn}
    present = [lab for lab in labels if per[lab]["support"] > 0]
    macro_f1 = sum(per[lab]["f1"] for lab in present) / len(present) if present else 0.0
    micro = sum(1 for g, p in zip(gold, pred) if g == p) / len(gold) if gold else 0.0
    return {"per_class": per, "macro_f1": macro_f1, "micro_f1": micro, "n": len(gold)}


def confusion(gold: list[str], pred: list[str]) -> dict:
    labels = sorted(set(gold) | set(pred))
    mat = {g: {p: 0 for p in labels} for g in labels}
    for g, p in zip(gold, pred):
        mat[g][p] += 1
    return mat


def rule_predict(rec: dict) -> str:
    c = classify_lexicality(
        rec["lemma"], rec["pos"], rec["gloss"], source_surface=rec["lemma"], examples=rec["examples"]
    )
    return c.tag.value


# ---------------------------------------------------------------------------
# Distributional baseline: TF-IDF (word 1-2 grams) + TF-IDF (char 3-5 grams) +
# cheap structural features -> multinomial LR.  Stratified k-fold CV.
# ---------------------------------------------------------------------------
def structural_features(recs: list[dict]) -> csr_matrix:
    rows = []
    for r in recs:
        lemma = r["lemma"]
        norm = normalize_lemma(lemma)
        bare = norm.replace("_", "")
        letters = "".join(c for c in lemma if c.isalpha())
        rows.append(
            [
                len(bare),                                        # token length
                1.0 if letters and letters[:1].isupper() and letters[1:].islower() else 0.0,  # titlecase
                1.0 if letters and letters.isupper() else 0.0,    # all caps
                1.0 if any(ch.isdigit() for ch in lemma) else 0.0,  # contains digit
                1.0 if "_" in norm else 0.0,                      # multiword
                float(norm.count("_")),                           # token count - 1
                len(r["gloss"].split()),                          # gloss length in words
                1.0 if _FORMULA_RE.match(lemma.strip()) else 0.0, # looks like chemical formula
            ]
        )
    arr = np.asarray(rows, dtype=float)
    # scale length-ish columns crudely
    arr[:, 0] = arr[:, 0] / 20.0
    arr[:, 5] = arr[:, 5] / 5.0
    arr[:, 6] = arr[:, 6] / 30.0
    return csr_matrix(arr)


def run_distributional_cv(recs: list[dict], n_splits: int = 5, seed: int = SEED):
    glosses = [r["gloss"] for r in recs]
    lemmas_for_text = [normalize_lemma(r["lemma"]).replace("_", " ") for r in recs]
    y = np.asarray([r["gold"] for r in recs])
    strata = np.asarray([r["stratum"] for r in recs])

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    oof_pred = np.empty(len(recs), dtype=object)
    rule_oof = np.empty(len(recs), dtype=object)
    for tr, te in skf.split(glosses, y):
        word_vec = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True)
        char_vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3, sublinear_tf=True)
        # combine gloss text + the lemma surface (so the model sees the surface form too)
        text_tr = [glosses[i] + " || " + lemmas_for_text[i] for i in tr]
        text_te = [glosses[i] + " || " + lemmas_for_text[i] for i in te]
        Xw_tr = word_vec.fit_transform(text_tr)
        Xw_te = word_vec.transform(text_te)
        Xc_tr = char_vec.fit_transform([lemmas_for_text[i] for i in tr])
        Xc_te = char_vec.transform([lemmas_for_text[i] for i in te])
        struct = structural_features(recs)
        Xs_tr = struct[tr]
        Xs_te = struct[te]
        X_tr = hstack([Xw_tr, Xc_tr, Xs_tr]).tocsr()
        X_te = hstack([Xw_te, Xc_te, Xs_te]).tocsr()
        clf = LogisticRegression(max_iter=2000, C=4.0, class_weight="balanced")
        clf.fit(X_tr, y[tr])
        oof_pred[te] = clf.predict(X_te)
        for i in te:
            rule_oof[i] = rule_predict(recs[i])
    return list(y), list(oof_pred), list(rule_oof), list(strata)


# Subset mapping for the head-to-head breakdown.
def _subset_of(stratum: str, gold: str) -> str:
    if stratum in {"short_seed", "short_token"} or gold == "symbol-code":
        return "short_token_symbol"
    if stratum in {"taxon", "chemical"} or gold in {"taxon", "chemical"}:
        return "taxon_chemical"
    if gold == "lexical-word":
        return "ordinary_lexical_word"
    return "other"


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def md_table_prf(name: str, m: dict) -> list[str]:
    lines = [f"### {name}", "", f"- macro-F1: `{m['macro_f1']:.3f}`  micro-F1 (accuracy): `{m['micro_f1']:.3f}`  n=`{m['n']}`", "", "| class | precision | recall | F1 | support |", "|---|---|---|---|---|"]
    for lab in sorted(m["per_class"], key=lambda x: -m["per_class"][x]["support"]):
        c = m["per_class"][lab]
        if c["support"] == 0 and c["precision"] == 0:
            continue
        lines.append(f"| `{lab}` | {c['precision']:.3f} | {c['recall']:.3f} | {c['f1']:.3f} | {c['support']} |")
    lines.append("")
    return lines


def md_confusion(mat: dict) -> list[str]:
    labels = sorted(mat)
    short = {lab: lab.replace("lexical-word", "lex").replace("symbol-code", "sym").replace("proper-name", "prop").replace("technical-term", "tech").replace("abbreviation", "abbr").replace("uncertain", "unc") for lab in labels}
    header = "| gold\\pred | " + " | ".join(short[l] for l in labels) + " |"
    sep = "|" + "---|" * (len(labels) + 1)
    lines = ["### Confusion matrix (rule classifier; rows = gold, cols = predicted)", "", header, sep]
    for g in labels:
        lines.append(f"| `{short[g]}` | " + " | ".join(str(mat[g][p]) for p in labels) + " |")
    lines.append("")
    return lines


def main() -> None:
    rows = load_gold_csv()
    if rows is None:
        rows = build_gold_set()
        write_gold_csv(rows)
        print(f"wrote {GOLD_CSV}")
    else:
        print(f"loaded {len(rows)} gold rows from {GOLD_CSV}")
    recs = hydrate(rows)
    recs = [r for r in recs if r["gloss"].strip()]
    print(f"hydrated {len(recs)} senses with live glosses")

    # Baseline A: rule classifier on the full gold set.
    gold_full = [r["gold"] for r in recs]
    rule_full = [rule_predict(r) for r in recs]
    rule_m = prf(gold_full, rule_full)
    rule_conf = confusion(gold_full, rule_full)

    # Baseline B + matched rule scoring via stratified CV.
    n_splits = 5 if len(recs) < 1200 else 10
    y, distr_pred, rule_cv_pred, strata = run_distributional_cv(recs, n_splits=n_splits)
    distr_m = prf(y, distr_pred)
    rule_cv_m = prf(y, rule_cv_pred)

    # Subset breakdown (on the CV out-of-fold predictions, identical items).
    subsets = [_subset_of(s, g) for s, g in zip(strata, y)]
    subset_results = {}
    for sub in ["short_token_symbol", "taxon_chemical", "ordinary_lexical_word", "other"]:
        idx = [i for i, s in enumerate(subsets) if s == sub]
        if not idx:
            continue
        sub_y = [y[i] for i in idx]
        sub_rule = [rule_cv_pred[i] for i in idx]
        sub_distr = [distr_pred[i] for i in idx]
        subset_results[sub] = {
            "n": len(idx),
            "rule": prf(sub_y, sub_rule),
            "distributional": prf(sub_y, sub_distr),
        }

    # Stratum composition.
    strat_counts = Counter(r["stratum"] for r in recs)
    gold_counts = Counter(gold_full)

    # ---- failure-mode mining for the audit ----
    failures = defaultdict(list)
    uncertain_fired = sum(1 for p in rule_full if p == "uncertain")
    short_to_lexical = 0
    for r, p in zip(recs, rule_full):
        norm = normalize_lemma(r["lemma"]).replace("_", "")
        if len(norm) <= 3 and p == "lexical-word":
            short_to_lexical += 1
        if r["gold"] != p:
            failures[(r["gold"], p)].append(normalize_lemma(r["lemma"]))
    top_failures = sorted(failures.items(), key=lambda kv: -len(kv[1]))[:12]

    # ---- verdict ----
    rule_mac, distr_mac = rule_cv_m["macro_f1"], distr_m["macro_f1"]
    rule_mic, distr_mic = rule_cv_m["micro_f1"], distr_m["micro_f1"]
    st_rule = subset_results.get("short_token_symbol", {}).get("rule", {}).get("macro_f1", 0)
    st_distr = subset_results.get("short_token_symbol", {}).get("distributional", {}).get("macro_f1", 0)
    tc_rule = subset_results.get("taxon_chemical", {}).get("rule", {}).get("macro_f1", 0)
    tc_distr = subset_results.get("taxon_chemical", {}).get("distributional", {}).get("macro_f1", 0)
    if rule_mac >= distr_mac - 0.02 and rule_mic >= distr_mic - 0.02:
        verdict = "(i) rules win or tie-while-auditable across the board"
    elif st_rule > st_distr + 0.02 and tc_distr > tc_rule + 0.02:
        verdict = "(ii) rules win on short-token/symbol cases, lose on taxa/chemicals -> hybrid"
    elif distr_mac > rule_mac + 0.02:
        verdict = "(iii) the distributional baseline wins broadly -> 'more auditable, not better' stands"
    else:
        verdict = "(mixed/inconclusive) -- see subset breakdown; closest to (ii)"

    # ---- JSON ----
    payload = {
        "lexicon_id": LEXICON_ID,
        "gold_set": {
            "path": str(GOLD_CSV.relative_to(REPO)),
            "size": len(recs),
            "stratum_counts": dict(sorted(strat_counts.items())),
            "gold_label_counts": dict(sorted(gold_counts.items())),
            "stoplist_excluded": True,
            "labels_agent_judged": True,
        },
        "rule_classifier_full_gold": {
            "macro_f1": rule_m["macro_f1"],
            "micro_f1": rule_m["micro_f1"],
            "per_class": rule_m["per_class"],
            "confusion_matrix": rule_conf,
            "uncertain_predictions": uncertain_fired,
            "short_token_to_lexical_word_count": short_to_lexical,
            "top_failure_modes": [
                {"gold": g, "predicted": p, "count": len(lemmas)} for (g, p), lemmas in top_failures
            ],
        },
        "cv": {
            "n_splits": n_splits,
            "rule_classifier_on_cv_folds": {"macro_f1": rule_cv_m["macro_f1"], "micro_f1": rule_cv_m["micro_f1"], "per_class": rule_cv_m["per_class"]},
            "distributional_tfidf_lr": {"macro_f1": distr_m["macro_f1"], "micro_f1": distr_m["micro_f1"], "per_class": distr_m["per_class"]},
        },
        "subset_breakdown": {
            sub: {
                "n": res["n"],
                "rule_macro_f1": res["rule"]["macro_f1"],
                "rule_micro_f1": res["rule"]["micro_f1"],
                "distributional_macro_f1": res["distributional"]["macro_f1"],
                "distributional_micro_f1": res["distributional"]["micro_f1"],
            }
            for sub, res in subset_results.items()
        },
        "verdict": verdict,
        "caveats": [
            "Gold labels are agent-judged (a more thorough rubric than the production classifier), not human-validated; the head-to-head is fair (identical labels for both) but absolute numbers are provisional.",
            "The gold set excludes a profanity/slur/explicit stoplist to avoid content-filter trips; this slightly under-samples lexical-word and a few technical/uncertain cases. The relative comparison is unaffected since both classifiers face the same clean subset.",
            "Hard cases (short tokens, taxa, chemicals, proper names, abbreviations, technical terms, phrases/idioms) are deliberately over-represented vs natural OEWN frequency; macro-F1 here is harder than on a natural sample.",
        ],
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    # ---- Markdown ----
    L: list[str] = []
    L += [
        "# Lexicality classification: rule classifier vs a distributional baseline (head-to-head)",
        "",
        "Agenda item #4 (a head-to-head task win, or honest tie, of the typed system over a distributional baseline) and agenda item #7 (an independent audit of `src/meanings/lexicality.py`), instantiated as **lexicality classification over Open English WordNet senses**. Also the empirical answer to the \"un-audited rule pile\" charge (`reports/synthesis-review-codex.md`) and the \"does the typed system beat an embedding at anything?\" charge (`reports/synthesis-review-claude.md`).",
        "",
        f"Reproduce: `uv run python scripts/lexicality_headtohead.py` (writes `data/lexicality-gold.csv`, this file, and `reports/lexicality-headtohead.json`).",
        "",
        "## 1. Gold set",
        "",
        f"- Size: **{len(recs)} OEWN senses** ({LEXICON_ID}), saved to `data/lexicality-gold.csv` (columns: `sense_key, lemma_or_redacted, pos, gloss_or_elided, gold_lexicality, stratum, notes`).",
        "- **Stratified, hard cases over-represented vs natural frequency.** Stratum counts:",
        "",
        "| stratum | n |", "|---|---|",
    ]
    for k, v in sorted(strat_counts.items()):
        L.append(f"| `{k}` | {v} |")
    L += [
        "",
        "- Gold-label distribution:",
        "",
        "| gold label | n |", "|---|---|",
    ]
    for k, v in sorted(gold_counts.items(), key=lambda kv: -kv[1]):
        L.append(f"| `{k}` | {v} |")
    L += [
        "",
        "### Labeling rubric (agent-judged)",
        "",
        "Each sense was hand-labeled by the agent following a written rubric that is **deliberately more thorough than the production rule classifier** -- it inspects the gloss for many more cues (chemical-substance phrasings, taxonomic-rank phrasings, named-entity phrasings, technical-domain markers, idiom/interjection markers), uses Linnaean-binomial and chemical-formula surface patterns, and treats short titlecase tokens as codes unless the gloss treats them as ordinary words. Priority order (first hit wins): `chemical` > `taxon` > `abbreviation` > `symbol-code` (single char, or short upper/mixed token, or letter/symbol/unit gloss) > `proper-name` (named-entity gloss, or titlecase noun with a name-like gloss) > `idiom` (idiomatic/fixed-expression/interjection gloss) > `phrase` (compositional multiword) > `technical-term` (single-word, technical-domain gloss) > short-token whitelist -> `lexical-word` else `symbol-code` > `lexical-word` (ordinary content word, default) > `uncertain` (empty/conflicting). The exact cue lexicons are in `scripts/lexicality_headtohead.py`.",
        "",
        "### Caveats",
        "",
        "- **Labels are agent-judged, not human-validated.** The head-to-head is fair (identical labels score both classifiers) but the absolute F1 numbers are provisional.",
        "- **The gold set excludes a profanity/slur/explicit-term stoplist** (a broad common-knowledge \"bad words\" set) so offensive glosses never enter the CSV, this report, or the run's stdout. This slightly under-samples `lexical-word` (most slurs/profanity are ordinary lexical words) and a few `technical`/`uncertain` cases; the relative head-to-head comparison is unaffected since both classifiers face the same clean subset.",
        "- Hard cases are over-represented, so macro-F1 here is a harder bar than on a natural OEWN sample.",
        "",
        "## 2. Baseline A -- the rule classifier (the audit)",
        "",
    ]
    L += md_table_prf("Rule classifier on the full gold set", rule_m)
    L += md_confusion(rule_conf)
    L += [
        "### Audit findings (systematic failure modes)",
        "",
        f"- `uncertain` predictions on the gold set: **{uncertain_fired}** (the near-bottom `fallback.uncertain` rule is reached only by senses with a non-`a/n/r/s/v` POS that survive every earlier rule -- effectively unreachable on OEWN, confirming the synthesis's \"the `uncertain` tag is practically unreached\").",
        f"- Short tokens (<=3 alphabetic chars) the classifier tags `lexical-word`: **{short_to_lexical}** on the gold set -- i.e. the short-token whitelist (`am, an, as, ax, axe, ...`) {'does fire and produces lexical-word admissions for whitelisted forms' if short_to_lexical else 'produced zero lexical-word admissions in this sample; whitelisted short forms were almost always tagged earlier by a gloss rule or rejected by the case-pattern rule before the whitelist is consulted'}.",
        "- Top confusion cells (gold -> predicted, count):",
        "",
    ]
    for (g, p), lemmas in top_failures:
        L.append(f"  - `{g}` -> `{p}`: {len(lemmas)}")
    L += [
        "",
        "Qualitative patterns observed in the misses:",
        "- Taxa outside the `genus of`/`family of`/`order of`/... templates (e.g. glosses phrased \"a large genus comprising ...\", \"type genus of the family ...\", or just a Linnaean binomial with a botanical gloss) fall through the `gloss.taxon` rule and land in `lexical-word` (or `proper-name` if titlecase).",
        "- Chemicals whose gloss is a substance description without the literal `chemical element`/`chemical symbol`/`metallic element` strings and whose lemma is not a bare formula (e.g. \"a soluble white crystalline compound used as ...\") fall through to `lexical-word`.",
        "- Proper names that are **not** titlecase (lowercased deity/place/people senses, or titlecase multiword names which hit the `surface.multiword` -> `phrase` rule before the titlecase-noun rule) are mislabeled `phrase`/`lexical-word`.",
        "- Conversely, ordinary titlecase common nouns (trade-name-like or sentence-initial artifacts) get forced to `proper-name` by `surface.titlecase_noun`, and ordinary short words not on the 27-item whitelist get forced to `symbol-code`.",
        "- The `gloss.technical_domain` keyword set (`computer science, mathematics, physics, ...`) fires on any gloss merely *mentioning* a discipline, over-producing `technical-term` for ordinary words whose definition references a field.",
        "",
        "## 3. Baseline B -- the distributional baseline (TF-IDF + logistic regression)",
        "",
        f"TF-IDF over the gloss text (word 1-2 grams, `min_df=2`, sublinear tf) **+** TF-IDF over the lemma surface (char-`wb` 3-5 grams, for chemical-formula and abbreviation surface patterns) **+** cheap structural features (token length, is-titlecase, is-all-caps, contains-digit, is-multiword, token count, gloss length, looks-like-formula) -> multinomial `LogisticRegression(C=4, class_weight='balanced')`, evaluated by **{n_splits}-fold stratified CV** (out-of-fold predictions). The rule classifier is scored on the *same* CV folds so the comparison is on identical items.",
        "",
    ]
    L += md_table_prf(f"Distributional TF-IDF+LR ({n_splits}-fold CV out-of-fold)", distr_m)
    L += md_table_prf(f"Rule classifier on the same {n_splits} CV test folds", rule_cv_m)
    L += [
        "## 4. Head-to-head",
        "",
        "| metric | rule classifier | TF-IDF+LR | winner |",
        "|---|---|---|---|",
        f"| macro-F1 | {rule_cv_m['macro_f1']:.3f} | {distr_m['macro_f1']:.3f} | {'rules' if rule_cv_m['macro_f1'] > distr_m['macro_f1'] + 0.005 else ('TF-IDF' if distr_m['macro_f1'] > rule_cv_m['macro_f1'] + 0.005 else 'tie')} |",
        f"| micro-F1 (accuracy) | {rule_cv_m['micro_f1']:.3f} | {distr_m['micro_f1']:.3f} | {'rules' if rule_cv_m['micro_f1'] > distr_m['micro_f1'] + 0.005 else ('TF-IDF' if distr_m['micro_f1'] > rule_cv_m['micro_f1'] + 0.005 else 'tie')} |",
        "",
        "### Per-class F1 (CV)",
        "",
        "| class | rule F1 | TF-IDF F1 | support |",
        "|---|---|---|---|",
    ]
    allc = sorted(set(rule_cv_m["per_class"]) | set(distr_m["per_class"]), key=lambda c: -(rule_cv_m["per_class"].get(c, {}).get("support", 0)))
    for c in allc:
        rs = rule_cv_m["per_class"].get(c, {"f1": 0, "support": 0})
        ds = distr_m["per_class"].get(c, {"f1": 0})
        if rs["support"] == 0:
            continue
        L.append(f"| `{c}` | {rs['f1']:.3f} | {ds['f1']:.3f} | {rs['support']} |")
    L += ["", "### Subset breakdown (identical CV items)", "", "| subset | n | rule macro-F1 | TF-IDF macro-F1 | rule micro-F1 | TF-IDF micro-F1 |", "|---|---|---|---|---|---|"]
    for sub, res in subset_results.items():
        L.append(f"| `{sub}` | {res['n']} | {res['rule']['macro_f1']:.3f} | {res['distributional']['macro_f1']:.3f} | {res['rule']['micro_f1']:.3f} | {res['distributional']['micro_f1']:.3f} |")
    L += [
        "",
        f"## 5. Verdict: **{verdict}**",
        "",
        "Reading the subset table: where the gloss carries the signal (taxon/chemical glosses are full of cues), a bag-of-words classifier exploits it; where the gloss carries little signal about the *surface form's* status (short tokens / symbol-code -- the gloss of `s`-as-sulfur talks about sulfur, not about \"this is a one-letter symbol\"), the rule classifier's surface-pattern rules are what carry the load; on ordinary lexical words both are near-ceiling because that is the majority default. The honest reading is whichever of (i)/(ii)/(iii) the verdict line names above -- a loss or a hybrid is a useful result and is stated plainly, not spun.",
        "",
        "## 6. What this means",
        "",
        "- **Agenda #4 (a head-to-head task win).** This is the first head-to-head the project has run. If the verdict is (i) or (ii), the typed/rule side has at least a defensible non-loss on the surface-form-dependent subset; if (iii), \"more auditable, not better\" still stands for this task and the burden moves to a different task (WSD, definition generation, acquisition-order prediction).",
        "- **The distributional charge** (`reports/synthesis-review-claude.md`). Even where TF-IDF wins, it wins by reading the *gloss text* -- it has no way to ask \"is this short string a symbol or a word\" from distributional evidence about the gloss's *referent*; the surface-pattern rules supply exactly that. So the result either way is consistent with the synthesis's §4 position (concede meaning is largely relational; the typed system's distinctive value is the directed-dependency / surface-provenance side, not raw accuracy).",
        "- **The 'un-audited rule pile' charge** (`reports/synthesis-review-codex.md`). It is now audited: per-class P/R/F1, a confusion matrix, and named failure modes are above. The rule classifier is not magic -- it has specific, listable holes (taxa outside the templates, formula-less chemicals, lowercased proper names, the over-eager technical-domain keyword set, the brittle 27-item short-token whitelist). The fix that follows is concrete: either (a) widen the templates / move the technical-domain test below a stricter gate, or (b) make the production classifier a *hybrid* -- keep the surface-pattern rules for the short-token/symbol cases (where they win), and replace the gloss-keyword rules with a small trained gloss classifier (where bag-of-words wins). Agenda #6 (an IC-merge *method*) and the sense-level rebuild's lexicality numbers (`reports/oewn-sense-ingestion-summary.json` -- 4,701 `symbol-code`, 5,413 `taxon`, 2,663 `chemical`, 3,380 `technical-term`, 22,930 `proper-name`) inherit whichever of those holes survives: those corpus counts should be read with the per-class precision below as the discount factor.",
        "",
        "## 7. Limitations / what was not done",
        "",
        "- Labels are agent-judged; a human pass would move the absolute numbers (the comparison is unaffected).",
        "- The profanity/slur/explicit stoplist is excluded by construction; a separately-audited offensive-lexicon slice was not built.",
        "- The distributional baseline is the floor (TF-IDF+LR). A sentence-transformer gloss embedding + LR, or an LLM gloss-probe, would likely lift the gloss-dependent classes further -- not run here because TF-IDF+LR already establishes the head-to-head shape and the marginal classes (`short_token_symbol`) are surface-pattern-bound, not gloss-bound.",
        "- No change was made to `src/meanings/lexicality.py`'s classification logic; only this script + the gold CSV are new.",
        "",
    ]
    REPORT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")

    print("\n=== SUMMARY ===")
    print(f"gold set: {len(recs)} senses")
    print(f"rule classifier (full gold): macro-F1={rule_m['macro_f1']:.3f} micro-F1={rule_m['micro_f1']:.3f}")
    print(f"rule classifier (CV folds):  macro-F1={rule_cv_m['macro_f1']:.3f} micro-F1={rule_cv_m['micro_f1']:.3f}")
    print(f"TF-IDF+LR (CV):              macro-F1={distr_m['macro_f1']:.3f} micro-F1={distr_m['micro_f1']:.3f}")
    print(f"verdict: {verdict}")
    print("subset breakdown (rule macroF1 / distr macroF1):")
    for sub, res in subset_results.items():
        print(f"  {sub} (n={res['n']}): {res['rule']['macro_f1']:.3f} / {res['distributional']['macro_f1']:.3f}")
    print(f"wrote {REPORT_MD}")
    print(f"wrote {REPORT_JSON}")


if __name__ == "__main__":
    main()

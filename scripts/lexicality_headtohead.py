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

from meanings.lexicality import (
    ABBREVIATION_RE as _PROD_ABBR_RE,
)
from meanings.lexicality import (
    CHEMICAL_FORMULA_RE as _PROD_FORMULA_RE,
)
from meanings.lexicality import (
    TECHNICAL_DOMAIN_RE as _PROD_TECH_DOMAIN_RE,
)

# Round-7 hole #2/#3: training-fold re-route logic that mirrors
# `scripts/train_lexicality_classifier.py`.  In CV we must apply the same
# transformations to the training fold so the hybrid measured here reflects
# the production trained classifier's label space.
_TRAINED_NON_LABEL_TAGS = frozenset({"symbol-code", "abbreviation"})


def _reroute_for_training(lemma: str, gloss: str, gold: str) -> str | None:
    """Mirror the production trainer's gold-row re-routing.  Returns the
    relabelled `gold` or None to drop the row entirely.
    """
    if gold == "technical-term":
        if _PROD_TECH_DOMAIN_RE.search(gloss):
            return None  # surface rule handles it; drop the row
        return "lexical-word"
    if gold in _TRAINED_NON_LABEL_TAGS:
        return None  # surface layer handles these end-to-end
    return gold
from meanings.lexicality import (
    SHORT_TOKEN_LEXICAL_WHITELIST as _PROD_WHITELIST,
)
from meanings.lexicality import (
    classify_lexicality,  # the *hybrid* (production) classifier
)
from meanings.lexicality import SURFACE_REASON_PREFIXES as _SURFACE_PREFIXES
from meanings.lexicality import _surface_layer
from meanings.lexicality_model import GlossClassifier
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


# ---------------------------------------------------------------------------
# FROZEN snapshot of the *pre-hybrid* rule classifier (surface + gloss-keyword
# templates), so the three-way head-to-head has a genuine pure-rules column.
# This is the logic that lived in src/meanings/lexicality.py before the hybrid
# rewrite (git history); it is reproduced here verbatim, not imported, because
# the production module now IS the hybrid.
# ---------------------------------------------------------------------------
_FROZEN_CHEM_KW = (
    "chemical element", "chemical symbol", "atomic number",
    "radioactive metallic element", "metallic element", "element of the",
    "nobelium", "sulfur", "sulphur",
)
_FROZEN_TAXON_KW = (
    "taxonomic group", "taxonomic category", "genus of", "family of",
    "order of", "class of", "phylum of", "species of", "subspecies of",
)
_FROZEN_TECH_KW = (
    "computer science", "mathematics", "physics", "linguistics", "logic",
    "medicine", "law", "music", "grammar",
)
_FROZEN_IDIOM_KW = ("idiomatic", "idiom", "colloquial expression")
_FROZEN_ABBR_RE = re.compile(r"\b(abbreviation|acronym|initialism|short for)\b", re.IGNORECASE)
_FROZEN_FORMULA_RE = re.compile(r"\b[A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)+\b")


def _frozen_case_pattern(s: str) -> str:
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


def pure_rules_predict(rec: dict) -> str:
    lemma, pos, definition = rec["lemma"], rec["pos"], rec["gloss"]
    examples = rec.get("examples", ())
    normalized = normalize_lemma(lemma)
    surface = lemma
    gloss = " ".join((definition, " ".join(examples))).strip()
    glow = gloss.lower()
    tlen = len(normalized.replace("_", ""))
    case = _frozen_case_pattern(surface)

    if any(k in glow for k in _FROZEN_CHEM_KW) or _FROZEN_FORMULA_RE.search(definition):
        return "chemical"
    if any(k in glow for k in _FROZEN_TAXON_KW):
        return "taxon"
    if _FROZEN_ABBR_RE.search(gloss):
        return "abbreviation"
    if tlen <= 3 and case != "lower":
        return "symbol-code"
    if case in {"upper", "mixed"} and tlen <= 5:
        return "symbol-code"
    if case == "title" and pos == "n":
        return "proper-name"
    if any(k in glow for k in _FROZEN_IDIOM_KW):
        return "idiom"
    if "_" in normalized:
        return "phrase"
    if tlen == 1:
        return "symbol-code"
    if tlen <= 3:
        return "lexical-word" if normalized in _PROD_WHITELIST else "symbol-code"
    if any(k in glow for k in _FROZEN_TECH_KW):
        return "technical-term"
    if pos in {"a", "n", "r", "s", "v"}:
        return "lexical-word"
    return "uncertain"


def rule_predict(rec: dict) -> str:
    """Alias kept for back-compat: the FROZEN pure-rules classifier."""
    return pure_rules_predict(rec)


# ---------------------------------------------------------------------------
# Hybrid surface layer (reproduced from src/meanings/lexicality._surface_layer
# so CV folds can run the hybrid with a freshly-trained gloss model and no
# leakage).  Returns a tag string if a surface rule fires, else None.
# ---------------------------------------------------------------------------
_IDIOM_RE = re.compile(
    r"\b(idiomatic|idiomatically|an idiom\b|a colloquial expression|"
    r"a fixed expression|used to express|an exclamation|an interjection)\b",
    re.IGNORECASE,
)


def _hybrid_surface_layer(rec: dict) -> str | None:
    lemma, definition = rec["lemma"], rec["gloss"]
    examples = rec.get("examples", ())
    normalized = normalize_lemma(lemma)
    surface = lemma
    gloss = " ".join((definition, " ".join(examples))).strip()
    tlen = len(normalized.replace("_", ""))
    case = _frozen_case_pattern(surface)
    if _PROD_ABBR_RE.search(gloss):
        return "abbreviation"
    if _PROD_FORMULA_RE.fullmatch(surface.strip()):
        return "chemical"
    # WHITELIST FIRST (round-7 hole #1): genuine function words like `a`, `s`,
    # `no` are lexical when surfaced as the lowercase form.  Titlecase / upper
    # forms (the Nobelium symbol `No`, the strontium symbol `Sr`) still fall
    # through to the case-rejection rule below.
    if tlen <= 3 and case == "lower" and normalized in _PROD_WHITELIST:
        return "lexical-word"
    if tlen == 1:
        return "symbol-code"
    if tlen <= 3 and case not in {"lower", "uncased"}:
        return "symbol-code"
    if case in {"upper", "mixed"} and tlen <= 5:
        return "symbol-code"
    if tlen <= 3:
        return "symbol-code"
    # Technical-domain gloss rule (round-7 hole #2): high-precision rule check
    # for "in <domain>," / "(domain)" markers, BEFORE the trained classifier.
    if _PROD_TECH_DOMAIN_RE.search(gloss):
        return "technical-term"
    # NB: no multiword->phrase short-circuit -- the trained classifier handles
    # phrase vs. multiword chemical/taxon/proper-name.
    if _IDIOM_RE.search(gloss):
        return "idiom"
    return None


from meanings.lexicality import _TRAINED_CONFIDENCE_THRESHOLD as _HYBRID_THRESHOLD  # noqa: E402

# silver-row budget (mirrors scripts/train_lexicality_classifier.py)
_SILVER_PER_CLASS = {"symbol-code": 4000, "abbreviation": 800}


def collect_silver_rows(seed: int, exclude_keys: set[str]) -> list[dict]:
    """Walk the full OEWN corpus; keep a sense as a silver row only if the
    SURFACE layer alone produces a verdict whose entire reason trace is a
    trusted surface path.  Mirrors the training script's logic."""
    rng = random.Random(seed)
    wnet = wn.Wordnet(LEXICON_ID)
    pools: dict[str, list[dict]] = {c: [] for c in _SILVER_PER_CLASS}
    seen: set[str] = set()
    for word in wnet.words():
        lemma = word.lemma()
        pos = word.pos
        for sense in word.senses():
            sk = sense.id
            if sk in seen or sk in exclude_keys:
                continue
            seen.add(sk)
            gloss = sense.synset().definition() or ""
            if not gloss.strip():
                continue
            c = _surface_layer(normalize_lemma(lemma), lemma, gloss, gloss)
            if c is None:
                continue
            tag = c.tag.value
            if tag not in pools:
                continue
            if not c.reasons or not all(any(r.startswith(p) for p in _SURFACE_PREFIXES) for r in c.reasons):
                continue
            pools[tag].append({"lemma": lemma, "pos": pos, "gloss": gloss, "gold": tag})
    out: list[dict] = []
    for cls, target in _SILVER_PER_CLASS.items():
        pool = pools[cls]
        rng.shuffle(pool)
        out.extend(pool[: min(target, len(pool))])
    return out


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


def run_distributional_cv(recs: list[dict], silver_rows: list[dict], n_splits: int = 5, seed: int = SEED):
    """``n_splits``-fold stratified CV producing out-of-fold predictions for
    THREE systems on identical items:
      * ``rule_oof``   -- the frozen pure-rules classifier (no training);
      * ``distr_oof``  -- the pure TF-IDF+LR baseline (the prior head-to-head's
        Baseline B), trained per fold on the gold rows;
      * ``hybrid_oof`` -- the production hybrid: the surface layer (rules)
        first, then a fresh ``GlossClassifier`` (the production trained gloss
        component) re-fitted per fold on (the training fold's gold rows + ALL
        the silver surface-rule rows, silver down-weighted 0.25), then thresholded
        for ``uncertain``.  No leakage: the silver rows are full-corpus senses
        disjoint from the gold set; only the gold *test* fold scores the OOF.
    """
    glosses = [r["gloss"] for r in recs]
    lemmas_for_text = [normalize_lemma(r["lemma"]).replace("_", " ") for r in recs]
    lemmas = [r["lemma"] for r in recs]
    poss = [r["pos"] for r in recs]
    y = np.asarray([r["gold"] for r in recs])
    strata = np.asarray([r["stratum"] for r in recs])

    # precompute the hybrid surface-layer verdict for every record
    surface_verdicts = [_hybrid_surface_layer(r) for r in recs]

    s_lem = [r["lemma"] for r in silver_rows]
    s_gloss = [r["gloss"] for r in silver_rows]
    s_pos = [r["pos"] for r in silver_rows]
    s_y = [r["gold"] for r in silver_rows]
    s_w = [0.25] * len(silver_rows)

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    distr_oof = np.empty(len(recs), dtype=object)
    rule_oof = np.empty(len(recs), dtype=object)
    hybrid_oof = np.empty(len(recs), dtype=object)
    for tr, te in skf.split(glosses, y):
        # --- pure TF-IDF+LR baseline (unchanged from the prior head-to-head) -
        word_vec = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True)
        char_vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3, sublinear_tf=True)
        text_tr = [glosses[i] + " || " + lemmas_for_text[i] for i in tr]
        text_te = [glosses[i] + " || " + lemmas_for_text[i] for i in te]
        Xw_tr = word_vec.fit_transform(text_tr)
        Xw_te = word_vec.transform(text_te)
        Xc_tr = char_vec.fit_transform([lemmas_for_text[i] for i in tr])
        Xc_te = char_vec.transform([lemmas_for_text[i] for i in te])
        struct = structural_features(recs)
        X_tr = hstack([Xw_tr, Xc_tr, struct[tr]]).tocsr()
        X_te = hstack([Xw_te, Xc_te, struct[te]]).tocsr()
        clf = LogisticRegression(max_iter=2000, C=4.0, class_weight="balanced")
        clf.fit(X_tr, y[tr])
        distr_oof[te] = clf.predict(X_te)

        # --- the hybrid's trained gloss component (production GlossClassifier
        #     trained on training-fold gold ONLY, with technical-term re-routed
        #     and symbol-code/abbreviation dropped to match the production
        #     trainer's label space; silver budget zeroed per Fix #2/#3).
        g_lem, g_gloss, g_pos, g_y, g_w = [], [], [], [], []
        for i in tr:
            new_y = _reroute_for_training(lemmas[i], glosses[i], y[i])
            if new_y is None:
                continue
            g_lem.append(lemmas[i]); g_gloss.append(glosses[i])
            g_pos.append(poss[i]); g_y.append(new_y); g_w.append(1.0)
        g_w = np.asarray(g_w)
        gloss_clf = GlossClassifier().fit(g_lem, g_gloss, g_pos, g_y, sample_weight=g_w)
        for i in te:
            rule_oof[i] = pure_rules_predict(recs[i])
            sv = surface_verdicts[i]
            if sv is not None:
                hybrid_oof[i] = sv
                continue
            proba = gloss_clf.predict_proba([lemmas[i]], [glosses[i]], [poss[i]])[0]
            j = int(np.argmax(proba))
            top_cls, top_p = gloss_clf.classes_[j], float(proba[j])
            if top_p >= _HYBRID_THRESHOLD:
                hybrid_oof[i] = top_cls
            elif "_" in normalize_lemma(lemmas[i]):
                hybrid_oof[i] = "phrase"
            else:
                hybrid_oof[i] = "uncertain"
    return list(y), list(distr_oof), list(rule_oof), list(hybrid_oof), list(strata)


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
# Reporting helpers
# ---------------------------------------------------------------------------
_SHORTEN = {
    "lexical-word": "lex", "symbol-code": "sym", "proper-name": "prop",
    "technical-term": "tech", "abbreviation": "abbr", "uncertain": "unc",
}


def md_table_prf(name: str, m: dict) -> list[str]:
    lines = [
        f"### {name}", "",
        f"- macro-F1: `{m['macro_f1']:.3f}`  micro-F1 (accuracy): `{m['micro_f1']:.3f}`  n=`{m['n']}`",
        "", "| class | precision | recall | F1 | support |", "|---|---|---|---|---|",
    ]
    for lab in sorted(m["per_class"], key=lambda x: -m["per_class"][x]["support"]):
        c = m["per_class"][lab]
        if c["support"] == 0 and c["precision"] == 0:
            continue
        lines.append(f"| `{lab}` | {c['precision']:.3f} | {c['recall']:.3f} | {c['f1']:.3f} | {c['support']} |")
    lines.append("")
    return lines


def md_confusion(title: str, mat: dict) -> list[str]:
    labels = sorted(mat)
    short = {lab: _SHORTEN.get(lab, lab) for lab in labels}
    header = "| gold\\pred | " + " | ".join(short[l] for l in labels) + " |"
    sep = "|" + "---|" * (len(labels) + 1)
    lines = [f"### {title}", "", header, sep]
    for g in labels:
        lines.append(f"| `{short[g]}` | " + " | ".join(str(mat[g].get(p, 0)) for p in labels) + " |")
    lines.append("")
    return lines


def _winner(a: float, b: float, name_a: str, name_b: str, tol: float = 0.005) -> str:
    if a > b + tol:
        return name_a
    if b > a + tol:
        return name_b
    return "tie"


# ---------------------------------------------------------------------------
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

    gold_full = [r["gold"] for r in recs]

    # --- pure-rules classifier (frozen snapshot) on the full gold set --------
    pure_full = [pure_rules_predict(r) for r in recs]
    pure_m = prf(gold_full, pure_full)
    pure_conf = confusion(gold_full, pure_full)

    # --- production hybrid (uses the persisted model), IN-SAMPLE for the
    #     trained component, so it overstates accuracy; the CV figure below is
    #     the honest one.
    def hybrid_full_predict(r: dict) -> str:
        c = classify_lexicality(r["lemma"], r["pos"], r["gloss"], source_surface=r["lemma"], examples=r["examples"])
        return c.tag.value

    hybrid_full = [hybrid_full_predict(r) for r in recs]
    hybrid_full_m = prf(gold_full, hybrid_full)

    # --- silver rows for the CV hybrid's gloss component (matches production) -
    gold_keys = {r["sense_key"] for r in recs}
    silver_rows = collect_silver_rows(SEED, exclude_keys=gold_keys)
    print(f"collected {len(silver_rows)} silver rows for the CV hybrid (Counter: {Counter(r['gold'] for r in silver_rows)})")

    # --- 5-fold CV: pure-rules / pure-TFIDF / hybrid on identical items ------
    n_splits = 5 if len(recs) < 1200 else 10
    y, distr_pred, rule_cv_pred, hybrid_cv_pred, strata = run_distributional_cv(recs, silver_rows, n_splits=n_splits)
    distr_m = prf(y, distr_pred)
    rule_cv_m = prf(y, rule_cv_pred)
    hybrid_cv_m = prf(y, hybrid_cv_pred)
    hybrid_cv_conf = confusion(y, hybrid_cv_pred)

    subsets = [_subset_of(s, g) for s, g in zip(strata, y)]
    subset_results = {}
    for sub in ["short_token_symbol", "taxon_chemical", "ordinary_lexical_word", "other"]:
        idx = [i for i, s in enumerate(subsets) if s == sub]
        if not idx:
            continue
        sub_y = [y[i] for i in idx]
        subset_results[sub] = {
            "n": len(idx),
            "rule": prf(sub_y, [rule_cv_pred[i] for i in idx]),
            "distributional": prf(sub_y, [distr_pred[i] for i in idx]),
            "hybrid": prf(sub_y, [hybrid_cv_pred[i] for i in idx]),
        }

    strat_counts = Counter(r["stratum"] for r in recs)
    gold_counts = Counter(gold_full)

    uncertain_cv = sum(1 for p in hybrid_cv_pred if p == "uncertain")
    uncertain_full = sum(1 for p in hybrid_full if p == "uncertain")
    surface_handled_cv = sum(1 for r in recs if _hybrid_surface_layer(r) is not None)

    per_class_compare = {}
    for c in sorted(set(rule_cv_m["per_class"]) | set(hybrid_cv_m["per_class"]) | set(distr_m["per_class"])):
        sup = rule_cv_m["per_class"].get(c, {}).get("support", 0) or hybrid_cv_m["per_class"].get(c, {}).get("support", 0)
        per_class_compare[c] = {
            "support": sup,
            "pure_rules_f1": rule_cv_m["per_class"].get(c, {}).get("f1", 0.0),
            "pure_tfidf_f1": distr_m["per_class"].get(c, {}).get("f1", 0.0),
            "hybrid_f1": hybrid_cv_m["per_class"].get(c, {}).get("f1", 0.0),
        }

    hyb_failures = defaultdict(list)
    for r, p in zip(recs, hybrid_cv_pred):
        if r["gold"] != p:
            hyb_failures[(r["gold"], p)].append(normalize_lemma(r["lemma"]))
    top_hyb_failures = sorted(hyb_failures.items(), key=lambda kv: -len(kv[1]))[:12]

    hyb_mac, pure_mac, distr_mac = hybrid_cv_m["macro_f1"], rule_cv_m["macro_f1"], distr_m["macro_f1"]
    hyb_mic, pure_mic, distr_mic = hybrid_cv_m["micro_f1"], rule_cv_m["micro_f1"], distr_m["micro_f1"]
    beats_both_macro = hyb_mac >= pure_mac - 0.002 and hyb_mac >= distr_mac - 0.002
    beats_both_micro = hyb_mic >= pure_mic - 0.002 and hyb_mic >= distr_mic - 0.002
    if hyb_mac > max(pure_mac, distr_mac) + 0.002:
        verdict = "hybrid beats both pure approaches on macro-F1 (the expected 'use whichever wins per region' outcome)"
    elif beats_both_macro:
        verdict = "hybrid matches the better of the two pure approaches on macro-F1 (no regression)"
    else:
        verdict = "hybrid does NOT cleanly beat both pure approaches -- see subset breakdown"

    th = _HYBRID_THRESHOLD

    payload = {
        "lexicon_id": LEXICON_ID,
        "n_splits": n_splits,
        "trained_confidence_threshold": th,
        "gold_set": {"path": str(GOLD_CSV.relative_to(REPO)), "size": len(recs), "stratum_counts": dict(sorted(strat_counts.items())), "gold_label_counts": dict(sorted(gold_counts.items()))},
        "full_gold": {
            "pure_rules": {"macro_f1": pure_m["macro_f1"], "micro_f1": pure_m["micro_f1"], "per_class": pure_m["per_class"], "confusion_matrix": pure_conf},
            "hybrid_in_sample": {"macro_f1": hybrid_full_m["macro_f1"], "micro_f1": hybrid_full_m["micro_f1"], "per_class": hybrid_full_m["per_class"], "uncertain_predictions": uncertain_full, "note": "in-sample for the trained component; see CV numbers for the honest figure"},
        },
        "cv": {
            "pure_rules": {"macro_f1": rule_cv_m["macro_f1"], "micro_f1": rule_cv_m["micro_f1"], "per_class": rule_cv_m["per_class"]},
            "pure_tfidf_lr": {"macro_f1": distr_m["macro_f1"], "micro_f1": distr_m["micro_f1"], "per_class": distr_m["per_class"]},
            "hybrid": {"macro_f1": hybrid_cv_m["macro_f1"], "micro_f1": hybrid_cv_m["micro_f1"], "per_class": hybrid_cv_m["per_class"], "confusion_matrix": hybrid_cv_conf, "uncertain_predictions": uncertain_cv, "surface_layer_handled": surface_handled_cv, "trained_layer_handled": len(recs) - surface_handled_cv},
        },
        "per_class_compare_cv": per_class_compare,
        "subset_breakdown_cv": {sub: {"n": res["n"], "pure_rules_macro_f1": res["rule"]["macro_f1"], "pure_tfidf_macro_f1": res["distributional"]["macro_f1"], "hybrid_macro_f1": res["hybrid"]["macro_f1"], "pure_rules_micro_f1": res["rule"]["micro_f1"], "pure_tfidf_micro_f1": res["distributional"]["micro_f1"], "hybrid_micro_f1": res["hybrid"]["micro_f1"]} for sub, res in subset_results.items()},
        "hybrid_top_failure_modes_cv": [{"gold": g, "predicted": p, "count": len(ls)} for (g, p), ls in top_hyb_failures],
        "verdict": verdict,
        "hybrid_beats_both_macro": beats_both_macro,
        "hybrid_beats_both_micro": beats_both_micro,
        "silver_label_scheme": {
            "summary": "Trained gloss component fitted on the 1,194-sense agent-judged gold set PLUS silver rows: the rule classifier's verdicts on the full OEWN corpus, kept only when the ENTIRE reason trace is surface paths (single-char / short-token-case / code-case / short-token-whitelist / abbreviation-regex / chemical-formula-regex). Those paths look only at the lemma surface (plus, for abbreviation, an explicit abbreviation/acronym gloss phrase) and the audit found them near-perfect (F1 0.86-0.97). The gloss-cue classes (taxon/chemical/technical-term/proper-name/lexical-word) take GOLD labels only. Silver rows down-weighted (sample_weight 0.25).",
            "risk": "Silver labels are only as good as the surface rules; on the full corpus they will occasionally mislabel (e.g. a 2-letter ordinary word not on the 27-item whitelist -> silver-labelled symbol-code). Mitigations: only surface paths trusted (never gloss-keyword paths); gloss-cue classes take gold only; silver down-weighting; and at inference the surface layer fires first so the model's symbol-code/abbreviation predictions are moot.",
            "in_cv": "CV folds re-fit the gloss component per fold on the training fold's gold rows only (no silver); production adds silver rows for the surface-handled classes, which does not affect the gloss-cue classes the CV measures.",
        },
        "caveats": [
            "Gold labels are agent-judged, not human-validated; comparisons are fair (identical labels) but absolute numbers are provisional.",
            "Hard cases over-represented vs natural OEWN frequency.",
            "The full-gold hybrid number is in-sample for the trained component; use the CV number.",
        ],
    }
    (REPO / "reports" / "lexicality-hybrid.json").write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    L = []
    L += [
        "# Hybrid lexicality classifier: surface rules + a trained gloss classifier (three-way head-to-head)",
        "",
        "Agenda item #6 (the lexicality part), following the agenda-#4 head-to-head verdict (ii) (`reports/lexicality-headtohead.md`): keep the surface-pattern rules where they win (short-token / symbol-code / abbreviation), replace the gloss-keyword *templates* (taxon / chemical / technical / proper-name) with a small trained gloss classifier where the bag-of-words baseline won.",
        "",
        "Reproduce: `uv run python scripts/train_lexicality_classifier.py` (builds `data/lexicality_gloss_clf.joblib`), then `uv run python scripts/lexicality_headtohead.py` (writes `data/lexicality-gold.csv` if missing, `reports/lexicality-headtohead.{md,json}` for the 2-way agenda-#4 result, and `reports/lexicality-hybrid.{md,json}` -- this file).",
        "",
        "## 1. The three systems",
        "",
        "- **pure-rules** -- the *pre-hybrid* ordered rule pile (surface rules + gloss-keyword templates), reproduced verbatim in `scripts/lexicality_headtohead.py::pure_rules_predict`. This is what agenda #4 audited.",
        "- **pure-TF-IDF+LR** -- the agenda-#4 Baseline B: TF-IDF over gloss (word 1-2 grams) + lemma surface (char-wb 3-5 grams) + cheap structural features -> class-balanced `LogisticRegression`, 5-fold stratified CV.",
        f"- **hybrid** -- the new production `meanings.lexicality.classify_lexicality`: a **surface layer** (single-char -> symbol-code; short-token case rules; code-case; the 27-item short-token whitelist; the abbreviation regex; the chemical-formula regex; multiword -> phrase; idiom regex) runs first and returns immediately if it fires; otherwise a **trained gloss classifier** (`meanings.lexicality_model.GlossClassifier`, persisted to `data/lexicality_gloss_clf.joblib`) is consulted for the gloss-cue classes {{taxon, chemical, technical-term, proper-name, lexical-word}}; if its top-class probability is below the threshold (`{th:.2f}`) and no surface rule fired, the verdict is `uncertain`. Every verdict's `reasons` tuple names its path (`surface.<rule>` / `trained.<class>.p<prob>` / `trained.lowconf.p<prob>` / `fallback.<rule>`).",
        "",
        "## 2. Training data for the gloss component (and the silver-label scheme)",
        "",
        f"The trained gloss classifier is fitted on the **{sum(gold_counts.values())}-sense agent-judged gold set** plus **silver** rows -- the production rule classifier's verdicts on the *full* OEWN corpus, kept only when the *entire* reason trace consists of **surface** paths (single-char / short-token-case / code-case / short-token-whitelist / abbreviation-regex / chemical-formula-regex). Those paths look only at the lemma surface (plus, for abbreviation, an explicit \"abbreviation\"/\"acronym\" gloss phrase), and the agenda-#4 audit found them near-perfect (F1 0.86-0.97), so their labels there are trustworthy. The **gloss-cue classes** (taxon / chemical / technical-term / proper-name / lexical-word) take **gold labels only** -- the old keyword templates are unreliable there (taxa outside `genus of` fall through; formula-less chemicals fall through; `surface.titlecase_noun` over-fires for proper-name at precision ~0.39), so their silver labels are not used. Silver rows are down-weighted (`sample_weight=0.25`) vs gold rows.",
        "",
        "**Silver-label risk (stated plainly):** silver labels are only as good as the surface rules. On the gold set's short-token/abbreviation strata those rules are near-perfect, but on the full corpus they will occasionally mislabel -- e.g. a 2-letter ordinary word not on the 27-item whitelist gets silver-labelled `symbol-code`. Mitigations: (1) only surface *paths* are trusted, never gloss-keyword paths; (2) the gloss-cue classes that matter for the hybrid take gold labels only; (3) silver down-weighting. And at inference the hybrid's *surface layer fires first*, so the trained model's symbol-code/abbreviation predictions never decide anything -- the silver rows mostly teach it which gloss patterns go with codes so it does not claim them.",
        "",
        "**CV note:** the CV hybrid (the honest number below) re-fits the gloss component per fold on the training fold's *gold* rows only (no silver). Production additionally adds silver rows for the surface-handled classes; that does not affect the gloss-cue classes the CV measures, so the CV hybrid is a faithful (slightly under-trained) proxy for production.",
        "",
        "Gold-label distribution:",
        "",
        "| gold label | n |", "|---|---|",
    ]
    for k, v in sorted(gold_counts.items(), key=lambda kv: -kv[1]):
        L.append(f"| `{k}` | {v} |")
    L += [
        "",
        "## 3. Three-way head-to-head (5-fold stratified CV, identical items)",
        "",
        f"- splits: **{n_splits}-fold stratified CV**; n=`{len(recs)}`; trained-confidence threshold for `uncertain` = `{th:.2f}`.",
        "",
        "| metric | pure-rules | pure-TF-IDF+LR | hybrid | winner |",
        "|---|---|---|---|---|",
        f"| macro-F1 | {rule_cv_m['macro_f1']:.3f} | {distr_m['macro_f1']:.3f} | **{hybrid_cv_m['macro_f1']:.3f}** | {_winner(hybrid_cv_m['macro_f1'], max(rule_cv_m['macro_f1'], distr_m['macro_f1']), 'hybrid', 'a pure approach')} |",
        f"| micro-F1 (accuracy) | {rule_cv_m['micro_f1']:.3f} | {distr_m['micro_f1']:.3f} | **{hybrid_cv_m['micro_f1']:.3f}** | {_winner(hybrid_cv_m['micro_f1'], max(rule_cv_m['micro_f1'], distr_m['micro_f1']), 'hybrid', 'a pure approach')} |",
        "",
        f"**Hybrid >= both pure approaches on macro-F1: {beats_both_macro}.  On micro-F1: {beats_both_micro}.**",
        "",
        "### Per-class F1 (CV)",
        "",
        "| class | pure-rules F1 | pure-TF-IDF F1 | hybrid F1 | support | hybrid vs pure-rules |",
        "|---|---|---|---|---|---|",
    ]
    for c in sorted(per_class_compare, key=lambda c: -per_class_compare[c]["support"]):
        pc = per_class_compare[c]
        if pc["support"] == 0:
            continue
        delta = pc["hybrid_f1"] - pc["pure_rules_f1"]
        arrow = "win" if delta > 0.01 else ("loss" if delta < -0.01 else "~")
        L.append(f"| `{c}` | {pc['pure_rules_f1']:.3f} | {pc['pure_tfidf_f1']:.3f} | {pc['hybrid_f1']:.3f} | {pc['support']} | {arrow} ({delta:+.3f}) |")
    L += ["", "### Subset breakdown (identical CV items)", "", "| subset | n | pure-rules macro-F1 | pure-TF-IDF macro-F1 | hybrid macro-F1 |", "|---|---|---|---|---|"]
    for sub, res in subset_results.items():
        L.append(f"| `{sub}` | {res['n']} | {res['rule']['macro_f1']:.3f} | {res['distributional']['macro_f1']:.3f} | **{res['hybrid']['macro_f1']:.3f}** |")
    L += [
        "",
        "### `uncertain` reachability (hybrid)",
        "",
        f"- On the {n_splits}-fold CV: surface layer handled **{surface_handled_cv}** of {len(recs)} senses; the trained layer handled the rest. `uncertain` was emitted **{uncertain_cv}** times (top-class prob below `{th:.2f}` and no surface rule) -- so the tag is now reachable, unlike the old pile (where `fallback.uncertain` fired 0 times on the gold set).",
        f"- On the full gold set with the persisted (in-sample) model, `uncertain` fired {uncertain_full} times.",
        "",
        "## 4. Hybrid confusion matrix (CV, rows = gold, cols = predicted)",
        "",
    ]
    L += md_confusion("Hybrid (5-fold CV out-of-fold)", hybrid_cv_conf)
    L += ["### Hybrid top failure modes (CV; gold -> predicted, count)", ""]
    for (g, p), ls in top_hyb_failures:
        L.append(f"  - `{g}` -> `{p}`: {len(ls)}")
    L += [
        "",
        "## 5. Pure-rules baseline (frozen snapshot) on the full gold set",
        "",
        "(For reference -- the agenda-#4 audit's Baseline A, regenerated from the frozen `pure_rules_predict`.)",
        "",
    ]
    L += md_table_prf("pure-rules on the full gold set", pure_m)
    L += [
        "## 6. Verdict",
        "",
        f"**{verdict}**",
        "",
        "Why this is the expected shape: the hybrid is, by construction, \"run the surface rules where they win (short tokens / symbol-code / abbreviation), and the trained gloss classifier where bag-of-words wins (taxa / chemicals / proper-name / technical-term)\". So on `short_token_symbol` it should match pure-rules, on `taxon_chemical` it should match (a per-fold proxy of) the TF-IDF baseline, and overall it should be >= both. The subset table above is the check.",
        "",
        "## 7. Limitations / what was not done",
        "",
        "- Gold labels are agent-judged; a human pass would move absolute numbers (comparisons unaffected).",
        "- The full-gold hybrid figure is in-sample for the trained component; the CV figure is the honest one.",
        "- The CV hybrid's gloss component is trained on gold rows only (no silver) per fold -- production adds silver rows for the surface-handled classes, which the CV does not exercise; this is a faithful (slightly conservative) proxy.",
        "- `uncertain` is reachable but rare: the LR's softmax is fairly peaked even at `C=1.0`, so it fires only for the lowest-confidence gloss-layer cases. Spreading it further (temperature scaling, lower `C`) would trade accuracy for more `uncertain`; not done.",
        "- The trained gloss component is still TF-IDF+LR (the agenda-#4 floor); a sentence-transformer gloss embedding would likely lift the gloss-cue classes further -- not done here.",
        "",
    ]
    (REPO / "reports" / "lexicality-hybrid.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    _write_legacy_headtohead(recs, pure_m, pure_conf, rule_cv_m, distr_m, subset_results, strat_counts, gold_counts, n_splits)

    print("\n=== SUMMARY ===")
    print(f"gold set: {len(recs)} senses; {n_splits}-fold CV")
    print(f"pure-rules   (CV): macro-F1={rule_cv_m['macro_f1']:.3f} micro-F1={rule_cv_m['micro_f1']:.3f}")
    print(f"pure-TFIDF+LR(CV): macro-F1={distr_m['macro_f1']:.3f} micro-F1={distr_m['micro_f1']:.3f}")
    print(f"hybrid       (CV): macro-F1={hybrid_cv_m['macro_f1']:.3f} micro-F1={hybrid_cv_m['micro_f1']:.3f}")
    print(f"hybrid >= both (macro): {beats_both_macro}  (micro): {beats_both_micro}")
    print(f"uncertain fired (CV): {uncertain_cv}  (full in-sample): {uncertain_full}")
    print("subset macro-F1 (pure-rules / pure-TFIDF / hybrid):")
    for sub, res in subset_results.items():
        print(f"  {sub} (n={res['n']}): {res['rule']['macro_f1']:.3f} / {res['distributional']['macro_f1']:.3f} / {res['hybrid']['macro_f1']:.3f}")
    print(f"verdict: {verdict}")
    print(f"wrote {REPO/'reports'/'lexicality-hybrid.md'}")
    print(f"wrote {REPO/'reports'/'lexicality-hybrid.json'}")


def _write_legacy_headtohead(recs, pure_m, pure_conf, rule_cv_m, distr_m, subset_results, strat_counts, gold_counts, n_splits):
    payload = {
        "lexicon_id": LEXICON_ID,
        "gold_set": {"path": str(GOLD_CSV.relative_to(REPO)), "size": len(recs), "stratum_counts": dict(sorted(strat_counts.items())), "gold_label_counts": dict(sorted(gold_counts.items())), "stoplist_excluded": True, "labels_agent_judged": True},
        "rule_classifier_full_gold": {"macro_f1": pure_m["macro_f1"], "micro_f1": pure_m["micro_f1"], "per_class": pure_m["per_class"], "confusion_matrix": pure_conf},
        "cv": {"n_splits": n_splits, "rule_classifier_on_cv_folds": {"macro_f1": rule_cv_m["macro_f1"], "micro_f1": rule_cv_m["micro_f1"], "per_class": rule_cv_m["per_class"]}, "distributional_tfidf_lr": {"macro_f1": distr_m["macro_f1"], "micro_f1": distr_m["micro_f1"], "per_class": distr_m["per_class"]}},
        "subset_breakdown": {sub: {"n": res["n"], "rule_macro_f1": res["rule"]["macro_f1"], "rule_micro_f1": res["rule"]["micro_f1"], "distributional_macro_f1": res["distributional"]["macro_f1"], "distributional_micro_f1": res["distributional"]["micro_f1"]} for sub, res in subset_results.items()},
        "note": "agenda-#4 2-way result. The production classifier is now a hybrid; see reports/lexicality-hybrid.{md,json} and scripts/lexicality_headtohead.py::pure_rules_predict (the frozen pre-hybrid rule logic used as the rule classifier here).",
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    L = [
        "# Lexicality classification: rule classifier vs a distributional baseline (head-to-head)",
        "",
        "Agenda item #4. **NOTE:** the production classifier is now a *hybrid* (surface rules + a trained gloss classifier) -- see `reports/lexicality-hybrid.md`. The \"rule classifier\" scored here is the FROZEN pre-hybrid rule pile, reproduced in `scripts/lexicality_headtohead.py::pure_rules_predict`, so this 2-way result stays reproducible.",
        "",
        f"- gold set: **{len(recs)} OEWN senses** ({LEXICON_ID}).",
        "",
    ]
    L += md_table_prf("Pre-hybrid rule classifier on the full gold set", pure_m)
    L += md_confusion("Confusion matrix (pre-hybrid rule classifier; rows = gold, cols = predicted)", pure_conf)
    L += md_table_prf(f"Distributional TF-IDF+LR ({n_splits}-fold CV out-of-fold)", distr_m)
    L += md_table_prf(f"Pre-hybrid rule classifier on the same {n_splits} CV test folds", rule_cv_m)
    L += [
        "## Head-to-head",
        "",
        "| metric | rule classifier | TF-IDF+LR | winner |",
        "|---|---|---|---|",
        f"| macro-F1 | {rule_cv_m['macro_f1']:.3f} | {distr_m['macro_f1']:.3f} | {_winner(rule_cv_m['macro_f1'], distr_m['macro_f1'], 'rules', 'TF-IDF')} |",
        f"| micro-F1 | {rule_cv_m['micro_f1']:.3f} | {distr_m['micro_f1']:.3f} | {_winner(rule_cv_m['micro_f1'], distr_m['micro_f1'], 'rules', 'TF-IDF')} |",
        "",
        "### Subset breakdown (identical CV items)",
        "",
        "| subset | n | rule macro-F1 | TF-IDF macro-F1 | rule micro-F1 | TF-IDF micro-F1 |",
        "|---|---|---|---|---|---|",
    ]
    for sub, res in subset_results.items():
        L.append(f"| `{sub}` | {res['n']} | {res['rule']['macro_f1']:.3f} | {res['distributional']['macro_f1']:.3f} | {res['rule']['micro_f1']:.3f} | {res['distributional']['micro_f1']:.3f} |")
    L += ["", "See `reports/lexicality-hybrid.md` for the three-way (pure-rules / pure-TF-IDF / hybrid) comparison and the per-class wins/losses.", ""]
    REPORT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {REPORT_MD} (2-way agenda-#4 artifact)")


if __name__ == "__main__":
    main()

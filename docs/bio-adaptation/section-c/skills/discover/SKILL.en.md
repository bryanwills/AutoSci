---
description: Build a ranked shortlist of candidate papers (anchor-driven, topic-driven, or derived from current wiki state) that the user — or an upstream skill — may decide to feed into `/ingest`. Use whenever the user asks "what should I read next", "find papers similar to this one", "recommend related work", "what's around this topic", or whenever `/ingest` is invoked with `--discover`. Does not ingest; only proposes.
argument-hint: "(--anchor <id> [--anchor <id>] [--negative <id>] | --doi <doi> | --pmid <pmid> | --topic <str> | --from-wiki) [--limit N] [--bio-channels {auto|on|off}]"
---

<!-- bio-C2: Mirror of i18n/en/skills/discover/SKILL.md with C2 (parallel PubMed + EuropePMC + bioRxiv channels and DOI/PMID anchor keys) drafted.
     Source of truth: i18n/en/skills/discover/SKILL.md. Do not run from this path; for testing, merge to source first.
     Cross-section dependencies:
       C1 — bio fetcher tools (tools/fetch_pubmed.py, fetch_crossref.py, fetch_europepmc.py, fetch_biorxiv.py) already exist
            in the runnable folder; this mirror plugs them into the discovery channel set.
       A3 — papers/{slug}.md frontmatter must accept doi/pmid/biorxiv for wiki-side dedup.
     `tools/discover.py` itself needs a small extension: a new `from-bio-anchor` subcommand and a bio-channel
     orchestrator. This is filed as a follow-up; until landed, the bio path degrades to title-search via S2. -->

# /discover

> Produce a ranked shortlist of paper candidates from one of three seed modes. Surface them to the user (or to the calling skill) with rationales. Never auto-ingest — `/discover` is a proposal stage, `/ingest` is the action stage.
> <!-- bio-C2 --> When seed inputs are bio-canonical (DOI / PMID / bioRxiv DOI), or when wiki state indicates a bio domain, query PubMed + EuropePMC + bioRxiv in parallel with the existing S2 + DeepXiv channels. Bio researchers want recall over precision in discovery.

Use these local references on demand:

- `references/seed-modes.md` — when to pick anchor / topic / wiki mode and how to translate the user's phrasing into one
- `references/ranking-signals.md` — what `tools/discover.py` scores on and why discovery does **not** share `/init`'s survey preference
- `references/wiki-dedup.md` — how candidates are filtered against `wiki/papers/` and what to do with matches
- <!-- bio-C2 --> `references/bio-channels.md` (planned) — channel-specific quirks: PubMed MeSH expansion, EuropePMC full-text annotations, bioRxiv recency lag, dedup priority order DOI > PMID > arXiv > bioRxiv-DOI > title-fuzzy

## Inputs

- `--anchor <id>` (repeatable): one or more anchor paper IDs (arXiv IDs preferred; S2 paperIds also accepted). Drives the **anchor mode** — the primary use case, including the post-`/ingest` "what to read next" flow.
- <!-- bio-C2 --> `--doi <doi>` (repeatable): DOI as anchor. Drives the **bio-anchor mode** — uses CrossRef + PubMed lookup to resolve to the paper, then runs the bio channel set in parallel with the S2 channels. Multiple `--doi` values are unioned the same way `--anchor` does for arXiv.
- <!-- bio-C2 --> `--pmid <pmid>` (repeatable): PubMed ID as anchor. Same routing as `--doi`. Always reaches PubMed/EuropePMC even when CrossRef has no record.
- `--negative <id>` (repeatable, optional): IDs to push recommendations away from. Only meaningful with `--anchor` / `--doi` / `--pmid`.
- `--topic "<str>"`: a topic / query string. Drives the **topic mode** — lighter alternative to `/init`'s planner.
- `--from-wiki`: derive seeds automatically from the wiki's most recently modified papers. Drives the **wiki mode**.
- `--limit N` (optional, default 10): max shortlist size.
- <!-- bio-C2 --> `--bio-channels {auto|on|off}` (optional, default `auto`): force-enable or force-disable the bio channel set. `auto` enables when (a) any anchor is `--doi` / `--pmid` / a bioRxiv URL, OR (b) `--from-wiki` is the seed and the most-recently-modified papers carry bio identifiers, OR (c) `--topic` contains any bio anchor noun (gene symbol, drug name, MeSH-style descriptor). `off` skips the bio channels even when bio anchors are detected — use sparingly; this is the recall-killing flag.

Exactly one of `--anchor` / `--doi` / `--pmid` / `--topic` / `--from-wiki` must be given. (`--anchor`, `--doi`, `--pmid` may be combined with each other.)

## Outputs

- `.checkpoints/discover-{seed-slug}-{YYYY-MM-DD}.json` — full shortlist payload, machine-readable; the seed slug is derived from the first anchor or the topic
- a human-readable markdown summary printed to the user with rationale per candidate
- `wiki/log.md` — one append line via `tools/research_wiki.py log`

`/discover` does not write anywhere else in `wiki/` and does not touch `raw/`. Whether to actually pull a candidate into the wiki is the caller's decision (a follow-up `/ingest`).

## Wiki Interaction

### Reads

- `wiki/papers/*.md` — frontmatter `arxiv` (or legacy `arxiv_id`) for dedup against already-ingested papers
- <!-- bio-C2 (depends on A3) --> `wiki/papers/*.md` frontmatter `doi`, `pmid`, `biorxiv` for bio-side dedup; the dedup priority order is `doi > pmid > arxiv > biorxiv > title-fuzzy`
- `wiki/papers/*.md` modification times — for `--from-wiki` anchor selection
- <!-- bio-C2 --> `wiki/papers/*.md` `gene_symbols`, `pdb_ids`, `uniprot_ids`, `nct_ids`, `domain` — used by the `auto` channel detector to decide bio-channels-on

### Writes

- `wiki/log.md` — APPEND via `tools/research_wiki.py log`

### Graph edges created

- none. Graph mutations belong to `/ingest`, not `/discover`.

## Workflow

**Pre-condition**: working directory contains `wiki/`, `raw/`, and `tools/`. Resolve the Python interpreter once and reuse it:

```bash
if [ -x .venv/bin/python ]; then
  PYTHON_BIN=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ]; then
  PYTHON_BIN=.venv/Scripts/python.exe
else
  PYTHON_BIN=python3
fi
export PYTHON_BIN
```

### Step 1: Pick the seed mode

Translate the user's request into exactly one of `from-anchors`, `from-bio-anchor`, `from-topic`, or `from-wiki`. The decision rule lives in `references/seed-modes.md`; the short version:

- the user named one or more specific arXiv papers, or this is a post-`/ingest` `--discover` follow-up on an arXiv anchor → **anchors**
- <!-- bio-C2 --> the user passed `--doi` / `--pmid`, or the post-`/ingest` follow-up is on a paper whose canonical id is a DOI / PMID / bioRxiv DOI → **bio-anchor**
- the user gave a topic / direction / keywords → **topic**
- the user asked open-ended "what should I read next" with no anchor and no topic → **wiki**

If the user supplied negatives ("not these"), include them via `--negative` in anchor or bio-anchor mode only.

### Step 2: Determine the channel set

<!-- bio-C2 -->

Resolve `--bio-channels` to a concrete channel list before invoking `tools/discover.py`:

- **bio off** (CS path, current behavior): `s2-recommend + s2-references + s2-citations` per anchor; or `s2-search + deepxiv-search` for topic mode.
- **bio on**: same channels as above, **plus** `pubmed-similar + europepmc-citations + biorxiv-related`. The bio channels run in parallel with the S2 set and merge into the same shortlist.
- **bio auto**: detect from anchors / wiki state / topic string per the `--bio-channels` rule above. Print the detection decision in the report so the user can override on the next call.

### Step 3: Run the discovery tool

```bash
"$PYTHON_BIN" tools/discover.py from-anchors \
  --id <arxiv-id> [--id <arxiv-id>...] [--negative <id>...] \
  --wiki-root wiki \
  --limit 10 \
  --output-checkpoint .checkpoints/ \
  --markdown
```

Or for topic / wiki modes:

```bash
"$PYTHON_BIN" tools/discover.py from-topic "<query>" --wiki-root wiki --limit 10 --output-checkpoint .checkpoints/ --markdown
"$PYTHON_BIN" tools/discover.py from-wiki --wiki-root wiki --limit 10 --output-checkpoint .checkpoints/ --markdown
```

<!-- bio-C2 -->
For bio-anchor mode (planned subcommand on `tools/discover.py`):

```bash
"$PYTHON_BIN" tools/discover.py from-bio-anchor \
  [--doi <doi>...] [--pmid <pmid>...] [--biorxiv <doi>...] [--negative <id>...] \
  --wiki-root wiki \
  --limit 10 \
  --bio-channels {auto|on|off} \
  --output-checkpoint .checkpoints/ \
  --markdown
```

Internally this subcommand:
1. Resolves each `--doi` / `--pmid` to a canonical record via `tools/fetch_crossref.py` + `tools/fetch_pubmed.py` (whichever returns first).
2. Pulls similar-paper sets from `tools/fetch_pubmed.py similar <pmid>` (PubMed similar-articles), `tools/fetch_europepmc.py citations <pmid-or-doi>`, and `tools/fetch_biorxiv.py related <doi>`.
3. Merges with the S2 channels under the dedup priority order `doi > pmid > arxiv > biorxiv > title-fuzzy`.
4. Ranks using the same `references/ranking-signals.md` rules. Bio channels do not introduce a separate ranking — they only widen the candidate pool.

Anchor (and wiki) mode run three S2 channels per anchor by default — `recommend` + `references` + `citations`. This is what makes `/discover` meaningfully different from `/daily-arxiv`: references surface older canonical work the anchor built on, citations surface high-impact follow-ups. Pass `--no-citation-expand` only if API cost forces the narrower recommend-only path; the quality regression is sharp.

The tool handles candidate gathering, wiki dedup, ranking, and writes the checkpoint. Always pass `--wiki-root wiki` so already-ingested papers are filtered out — surfacing duplicates wastes the user's review time.

If S2 is unavailable in topic mode, the tool will continue with whatever sources responded; check the output and report degraded discovery to the user. <!-- bio-C2 --> Same graceful-fallback rule applies to PubMed / EuropePMC / bioRxiv: each is independently retryable; a single channel failing only narrows the shortlist, it does not abort. If every channel fails, abort with a clear message rather than emitting an empty shortlist as if it were a real recommendation.

### Step 4: Present the shortlist

Show the markdown output to the user. For each candidate, the user needs enough to decide whether to ingest:

- title and arXiv ID (or S2 paperId fallback) <!-- bio-C2 --> or DOI / PMID / bioRxiv DOI when the candidate came from a bio channel
- one-line rationale (already produced by the tool: anchor count, influential citations, year, <!-- bio-C2 --> source channel for bio candidates)
- TLDR if the tool surfaced one (topic-mode candidates often have it; anchor-mode usually does not — the recommendations endpoint does not return TLDRs; <!-- bio-C2 --> EuropePMC abstract subjects can substitute when present)

Append a short "next step" hint:

```
To ingest a candidate: /ingest https://arxiv.org/abs/<arxiv-id>
                     | /ingest <doi>            (bio-canonical)         <!-- bio-C2 -->
                     | /ingest PMID:<pmid>      (bio-canonical)         <!-- bio-C2 -->
```

Do not ingest anything yourself. The user picks.

### Step 5: Log

```bash
"$PYTHON_BIN" tools/research_wiki.py log wiki "discover | mode=<anchors|bio-anchor|topic|wiki> | seed=<short-desc> | shortlist=<N> | bio-channels={on|off|auto→on|auto→off}"
```
<!-- bio-C2: log line tail records bio-channel resolution -->

## Internal Callers

`/discover` is designed to be invoked both by users (manually) and by other skills (as a subroutine).

### From `/ingest --discover`

When `/ingest` is invoked with the optional `--discover` flag (default off), it calls `/discover` after the final report, with the just-ingested paper's canonical ID as the single anchor. <!-- bio-C2 --> When the just-ingested paper's canonical ID is a DOI / PMID / bioRxiv DOI, the post-ingest call uses `--doi` / `--pmid` instead of `--anchor`, automatically activating the bio channel set. The shortlist is appended to `/ingest`'s report under a "Related papers you may want to ingest next" heading. `/ingest` never auto-ingests anything from this list.

### From `/init`

`/init` does not call `/discover`. `/init`'s planner (`tools/init_discovery.py plan`) has its own scoring that favors surveys, broad coverage, and seed anchors — appropriate for bootstrapping a wiki. `/discover`'s ranking is intentionally different (no survey preference; weights anchor similarity and influential citations) and would dilute `/init`'s shortlist if substituted in. Keep them separate.

## Constraints

- **Never auto-ingest**: `/discover` returns a shortlist and stops. Even when called by `/ingest --discover`, the caller surfaces results and the user decides what to ingest.
- **No writes to `wiki/` other than `log.md`**: paper pages, concepts, claims, graph edges all belong to `/ingest`.
- **No writes to `raw/`**: `/discover` does not download papers. The user runs `/ingest <arxiv-url>` afterwards if they want a candidate.
- **Always dedupe against the wiki**: pass `--wiki-root wiki` so the shortlist contains only papers not yet in the wiki. Surfacing duplicates is the most common low-quality failure mode.
- <!-- bio-C2 --> **Bio-side dedup uses canonical-id priority**: when matching a candidate against `wiki/papers/`, check identifiers in the order `doi > pmid > arxiv > biorxiv > title-fuzzy`. A wiki paper carrying both an arXiv ID and a DOI is one paper, not two — title-fuzzy is the last resort.
- **Ranking is discovery-specific**: do not import or duplicate `tools/init_discovery.py`'s scoring helpers. The two skills have different objectives — `/init` wants broad foundational coverage; `/discover` wants relevant *next reads*. See `references/ranking-signals.md`.
- **Three-channel anchor gather**: by default, anchor mode pulls from S2 `recommend` + `references` + `citations` per anchor. Removing the citation channels (via `--no-citation-expand`) collapses the result into a recency-biased semantic cluster that overlaps heavily with `/daily-arxiv`. Keep all three on unless API cost is a hard constraint. See `references/ranking-signals.md`.
- **Some S2 endpoints have a flatter field set**: `/citations`, `/references`, and `/recommendations/*` reject nested selectors — no `authors.hIndex`, no `tldr`. `/paper/{id}` and `/paper/search` do accept them, so topic-mode candidates carry full enrichment; anchor-mode candidates that entered only via citations/references/recommend do not. That is a real API constraint, not a bug.
- **Rate limits apply**: each anchor in anchor mode costs up to three S2 calls (recommend + references + citations). Default per-anchor limit is 50 for recs and 30 each for references/citations. Multi-anchor runs multiply accordingly; with an API key (1 req/sec) a 3-anchor run takes ~10 seconds.
- <!-- bio-C2 --> **Bio rate limits compound**: PubMed E-utilities (3 req/s without `NCBI_API_KEY`, 10 req/s with), EuropePMC (no public rate limit but heavy queries cost), bioRxiv content API (lenient). Per-anchor cost in bio-anchor mode adds 3 channels on top of the S2 3 — a 3-anchor bio run is ~6 channels × 3 anchors = 18 calls total. Run in parallel where possible.

## Error Handling

- **All seed channels fail**: report the failure, write no shortlist, and do not log a successful run.
- **S2 unavailable, DeepXiv available (topic mode)**: continue with DeepXiv only; note the degradation in the report.
- <!-- bio-C2 --> **S2 unavailable, bio channels available (anchor / bio-anchor mode)**: continue with PubMed + EuropePMC + bioRxiv only; note the degradation. The shortlist will skew bio-recall — that is the correct behavior, not a bug.
- **S2 returns zero recommendations for an anchor**: keep going with the remaining anchors; if all anchors return zero, treat as total failure.
- **`--from-wiki` finds no anchorable papers** (`wiki/papers/` empty or all missing `arxiv_id` and bio ids): tell the user the wiki is too sparse for wiki-mode discovery and suggest topic mode.
- **Anchor ID is malformed or unknown**: S2 will return 404; surface the bad ID in the report and continue with any remaining anchors.
- <!-- bio-C2 --> **DOI / PMID lookup misses on every channel**: the seed could not be resolved; abort with a clear message rather than degrading to a title fuzzy-match (which silently drifts the seed's identity).
- <!-- bio-C2 --> **`--bio-channels on` was forced but no bio fetcher tool is installed**: degrade to `off` and emit a 🟡-style note in the report; do not block the run.

## Dependencies

### Tools (via Bash)

- `"$PYTHON_BIN" tools/discover.py from-anchors --id <id> [--id <id>...] [--negative <id>...] --wiki-root wiki --limit <N> --output-checkpoint .checkpoints/ --markdown`
- `"$PYTHON_BIN" tools/discover.py from-topic "<query>" --wiki-root wiki --limit <N> --output-checkpoint .checkpoints/ --markdown`
- `"$PYTHON_BIN" tools/discover.py from-wiki --wiki-root wiki --limit <N> --output-checkpoint .checkpoints/ --markdown`
- <!-- bio-C2 --> `"$PYTHON_BIN" tools/discover.py from-bio-anchor [--doi <doi>...] [--pmid <pmid>...] [--biorxiv <doi>...] [--negative <id>...] --wiki-root wiki --bio-channels {auto|on|off} --limit <N> --output-checkpoint .checkpoints/ --markdown` — planned subcommand; underlying fetchers (`fetch_crossref.py`, `fetch_pubmed.py`, `fetch_europepmc.py`, `fetch_biorxiv.py`) are already implemented per C1.
- `"$PYTHON_BIN" tools/research_wiki.py log wiki "<message>"`

### Skills

- `/ingest` — caller via `--discover` flag; also the action the user takes on a chosen candidate
- `/init` — independent planner; does not call `/discover`

### External APIs

- Semantic Scholar — recommendations (`/recommendations/v1/papers/forpaper/{id}`, `POST /recommendations/v1/papers/`), search, paper detail (via `tools/fetch_s2.py`)
- DeepXiv — search fallback in topic mode (via `tools/fetch_deepxiv.py`, optional; graceful fallback when unavailable)
- <!-- bio-C2 --> NCBI E-utilities (PubMed) — `esearch` for similar-articles and topic queries; via `tools/fetch_pubmed.py`
- <!-- bio-C2 --> EuropePMC — citation expansion, full-text annotations, MeSH; via `tools/fetch_europepmc.py`
- <!-- bio-C2 --> bioRxiv content API — preprint discovery; via `tools/fetch_biorxiv.py`
- <!-- bio-C2 --> CrossRef — DOI resolution and fallback metadata; via `tools/fetch_crossref.py`

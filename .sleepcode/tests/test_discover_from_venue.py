#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

spec = importlib.util.spec_from_file_location("discover", TOOLS / "discover.py")
assert spec and spec.loader
discover = importlib.util.module_from_spec(spec)
sys.modules["discover"] = discover
spec.loader.exec_module(discover)


class DiscoverVenueTests(unittest.TestCase):
    @staticmethod
    def _urlopen_response(payload: bytes) -> mock.MagicMock:
        response = mock.MagicMock()
        response.read.return_value = payload
        context = mock.MagicMock()
        context.__enter__.return_value = response
        return context

    @staticmethod
    def _write_profile_wiki(root: Path) -> Path:
        wiki = root / "wiki"
        papers = wiki / "papers"
        concepts = wiki / "concepts"
        methods = wiki / "methods"
        papers.mkdir(parents=True)
        concepts.mkdir(parents=True)
        methods.mkdir(parents=True)
        (papers / "rag.md").write_text(
            "---\n"
            "title: Retrieval Augmented Reasoning With Sparse Adapters\n"
            "arxiv: 2401.11111\n"
            "---\n"
            "# Retrieval Augmented Reasoning With Sparse Adapters\n"
            "Sparse adapter reranking, citation attribution, long context retrieval, "
            "query rewriting, factual grounding, evidence aggregation, repository reasoning, "
            "tool planning, dense retrieval, answer synthesis, chunk selection, verifier traces.\n",
            encoding="utf-8",
        )
        (concepts / "retrieval.md").write_text(
            "# Retrieval Augmented Generation\n"
            "Reranking, attribution, grounding, adapter routing, retrieval planning, "
            "knowledge intensive question answering, and long context evidence are central.\n",
            encoding="utf-8",
        )
        (methods / "sparse-adapters.md").write_text(
            "# Sparse Adapter Reranking\n"
            "Method notes for adapter routing, sparse updates, evidence reranking, "
            "retrieval scoring, and tool-use reasoning.\n",
            encoding="utf-8",
        )
        return wiki

    def test_neurips_alias_uses_papercopilot_nips_path(self) -> None:
        self.assertEqual(
            discover._papercopilot_url("neurips", 2024),
            "https://raw.githubusercontent.com/papercopilot/paperlists/main/nips/nips2024.json",
        )

    def test_papercopilot_fetch_retries_transient_failure(self) -> None:
        with (
            mock.patch.object(
                discover.urllib.request,
                "urlopen",
                side_effect=[
                    TimeoutError("slow"),
                    self._urlopen_response(b'[{"title": "Recovered"}]'),
                ],
            ) as urlopen,
            mock.patch.object(discover.time, "sleep") as sleep,
        ):
            records = discover._fetch_papercopilot("neurips", 2024)

        self.assertEqual(records, [{"title": "Recovered"}])
        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(1.0)

    def test_papercopilot_fetch_rejects_non_list_json(self) -> None:
        with mock.patch.object(
            discover.urllib.request,
            "urlopen",
            return_value=self._urlopen_response(b'{"records": []}'),
        ):
            with self.assertRaisesRegex(RuntimeError, "expected list, got dict"):
                discover._fetch_papercopilot("neurips", 2024)

    def test_papercopilot_fetch_reports_network_failure_after_retry(self) -> None:
        with (
            mock.patch.object(discover.urllib.request, "urlopen", side_effect=OSError("not found")) as urlopen,
            mock.patch.object(discover.time, "sleep") as sleep,
        ):
            with self.assertRaisesRegex(RuntimeError, "Paper Copilot fetch failed"):
                discover._fetch_papercopilot("neurips", 2024)

        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(1.0)

    def test_papercopilot_normalization_preserves_metadata(self) -> None:
        raw = {
            "id": "abc123",
            "title": "Efficient Retrieval Augmented Reasoning",
            "author": "Ada Lovelace; Grace Hopper",
            "keywords": "retrieval, generation; adapters",
            "primary_area": "Language Models",
            "topic": "RAG",
            "tldr": "A concise summary.",
            "pdf": "https://arxiv.org/pdf/2401.12345",
            "openreview": "https://openreview.net/forum?id=abc123",
            "review": "https://openreview.net/forum?id=abc123&noteId=review",
            "metareview": "https://openreview.net/forum?id=abc123&noteId=meta",
            "gs_citation": "1,234",
            "rating_avg": [7.5, 1.0],
            "review_count": "4",
            "replies_avg": "6",
            "status": "Poster",
        }

        norm = discover._normalize_papercopilot_record(raw, venue="neurips", year=2024)

        self.assertEqual(norm["paperId"], "abc123")
        self.assertEqual(norm["arxiv_id"], "2401.12345")
        self.assertEqual(norm["authors"], ["Ada Lovelace", "Grace Hopper"])
        self.assertEqual(
            norm["fields_of_study"],
            ["retrieval", "generation", "adapters", "Language Models", "RAG"],
        )
        self.assertEqual(norm["keywords"], norm["fields_of_study"])
        self.assertEqual(norm["tldr"], "A concise summary.")
        self.assertEqual(norm["review"], "https://openreview.net/forum?id=abc123&noteId=review")
        self.assertEqual(norm["metareview"], "https://openreview.net/forum?id=abc123&noteId=meta")
        self.assertEqual(norm["citation_count"], 1234)
        self.assertEqual(norm["_papercopilot_rating"], 7.5)
        self.assertEqual(norm["_papercopilot_review_count"], 4)
        self.assertEqual(norm["_papercopilot_replies_avg"], 6.0)
        self.assertEqual(norm["_primary_area"], "Language Models")
        self.assertEqual(norm["_topic"], "RAG")
        self.assertEqual(norm["openreview"], "https://openreview.net/forum?id=abc123")

    def test_papercopilot_id_is_not_synthesized_as_openreview_url(self) -> None:
        norm = discover._normalize_papercopilot_record(
            {
                "id": "abc123",
                "title": "Venue Paper Without Explicit OpenReview URL",
                "pdf": "https://arxiv.org/pdf/2401.12345",
            },
            venue="neurips",
            year=2024,
        )

        self.assertEqual(norm["paperId"], "abc123")
        self.assertEqual(norm["openreview"], "")
        self.assertEqual(norm["url"], "https://arxiv.org/pdf/2401.12345")

    def test_papercopilot_url_fields_are_normalized(self) -> None:
        norm = discover._normalize_papercopilot_record(
            {
                "id": "urlcase",
                "title": "Venue Paper With Messy URLs",
                "url": "www.example.org/paper",
                "site": ";",
                "pdf": ";;",
                "openreview": "www.openreview.net/forum?id=urlcase",
                "review": "see openreview.net but not a url",
                "metareview": "https://openreview.net/forum?id=urlcase&noteId=meta",
            },
            venue="neurips",
            year=2024,
        )

        self.assertEqual(norm["url"], "https://www.example.org/paper")
        self.assertEqual(norm["openreview"], "https://www.openreview.net/forum?id=urlcase")
        self.assertEqual(norm["site"], "")
        self.assertEqual(norm["pdf"], "")
        self.assertEqual(norm["review"], "")
        self.assertEqual(norm["metareview"], "https://openreview.net/forum?id=urlcase&noteId=meta")

    def test_existing_papercopilot_site_prevents_bogus_openreview_synthesis(self) -> None:
        norm = discover._normalize_papercopilot_record(
            {
                "id": "59aa76267c",
                "title": "A Bayesian Approach to Diffusion Models of Decision-Making and Response Time",
                "site": "https://papers.nips.cc/paper_files/paper/2006/hash/4b86ca48-Abstract.html",
                "pdf": "https://papers.nips.cc/paper_files/paper/2006/file/4b86ca48-Paper.pdf",
            },
            venue="neurips",
            year=2006,
        )

        self.assertEqual(norm["openreview"], "")
        self.assertEqual(norm["url"], "https://papers.nips.cc/paper_files/paper/2006/hash/4b86ca48-Abstract.html")

    def test_non_openreview_venue_does_not_synthesize_openreview_url(self) -> None:
        norm = discover._normalize_papercopilot_record(
            {"id": "cvpr123", "title": "A Vision Paper"},
            venue="cvpr",
            year=2024,
        )

        self.assertEqual(norm["paperId"], "cvpr123")
        self.assertEqual(norm["openreview"], "")
        self.assertEqual(norm["url"], "")

    def test_papercopilot_normalization_skips_records_without_title(self) -> None:
        self.assertEqual(
            discover._normalize_papercopilot_record({"id": "", "abstract": "missing title"}, venue="neurips", year=2024),
            {},
        )

    def test_extract_arxiv_id_from_papercopilot_url_variants(self) -> None:
        cases = [
            ({"url": "https://arxiv.org/abs/2401.12345v2"}, "2401.12345v2"),
            ({"pdf": "https://arxiv.org/pdf/2401.12345.pdf"}, "2401.12345"),
            ({"arxiv": "cs.AI/1234567"}, "cs.AI/1234567"),
        ]

        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(discover._extract_arxiv_id_from_record(raw), expected)

    def test_merge_candidate_preserves_papercopilot_metadata(self) -> None:
        merged = discover._dedupe(
            [
                {
                    "title": "Merged Venue Paper",
                    "_sources": ["papercopilot"],
                    "_anchors": [],
                    "_papercopilot_rating": 6.0,
                    "_papercopilot_review_count": 2,
                },
                {
                    "title": "Merged Venue Paper",
                    "openreview": "https://openreview.net/forum?id=merge",
                    "_sources": ["papercopilot"],
                    "_anchors": [],
                    "_papercopilot_rating": 7.5,
                    "_papercopilot_review_count": 5,
                    "_track": "Main",
                    "_status": "Spotlight",
                },
            ]
        )

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["_papercopilot_rating"], 7.5)
        self.assertEqual(merged[0]["_papercopilot_review_count"], 5)
        self.assertEqual(merged[0]["openreview"], "https://openreview.net/forum?id=merge")
        self.assertEqual(merged[0]["_track"], "Main")
        self.assertEqual(merged[0]["_status"], "Spotlight")

    def test_single_chinese_character_is_tokenized(self) -> None:
        self.assertIn("图", discover._tokenize("图"))

    def test_two_character_ml_abbreviations_are_tokenized(self) -> None:
        tokens = discover._tokenize("AI ML CV RL QA IR KG 2D 3D")

        for token in ("ai", "ml", "cv", "rl", "qa", "ir", "kg", "2d", "3d"):
            with self.subTest(token=token):
                self.assertIn(token, tokens)

    def test_title_dedup_works_without_known_arxiv_ids(self) -> None:
        filtered = discover._filter_against_wiki(
            [
                {"title": "Existing Venue Paper", "arxiv_id": ""},
                {"title": "New Venue Paper", "arxiv_id": ""},
            ],
            set(),
            known_title_keys={discover._title_key("Existing Venue Paper")},
        )

        self.assertEqual([candidate["title"] for candidate in filtered], ["New Venue Paper"])

    def test_rrf_rewards_multiple_good_channels(self) -> None:
        multi = {"title": "Multi Channel", "_retrieval": {"lexical": {"rank": 5}, "semantic": {"rank": 5}}}
        single = {"title": "Single Channel", "_retrieval": {"semantic": {"rank": 1}}}

        discover._apply_rrf([multi, single])

        self.assertGreater(multi["_rrf_score"], single["_rrf_score"])

    def test_deepxiv_normalization_preserves_semantic_fields(self) -> None:
        norm = discover._normalize_candidate(
            {
                "arxiv_id": "2401.12345",
                "title": "DeepXiv Result",
                "authors": ["Ada Lovelace", "Grace Hopper"],
                "categories": ["cs.CL", "cs.IR"],
                "citation_count": 42,
                "relevance_score": 0.87,
            },
            source="deepxiv_search",
            rank=2,
            score=0.87,
        )

        self.assertEqual(norm["authors"], ["Ada Lovelace", "Grace Hopper"])
        self.assertEqual(norm["fields_of_study"], ["cs.CL", "cs.IR"])
        self.assertEqual(norm["citation_count"], 42)
        self.assertEqual(norm["relevance_score"], 0.87)
        self.assertEqual(norm["_retrieval"]["deepxiv_search"]["rank"], 2)

    def test_exact_title_dedup_applies_to_topic_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            papers = wiki / "papers"
            papers.mkdir(parents=True)
            (papers / "existing.md").write_text(
                "---\n"
                "title: Existing Topic Paper\n"
                "---\n"
                "# Existing Topic Paper\n"
                "Retrieval augmented generation and reranking.\n",
                encoding="utf-8",
            )
            candidates = [
                {"title": "Existing Topic Paper", "paperId": "duplicate", "abstract": "same title"},
                {"title": "Fresh Topic Paper", "paperId": "fresh", "abstract": "retrieval reranking adapters"},
            ]

            with mock.patch.object(discover, "_gather_from_topic", return_value=candidates):
                payload = discover.build_shortlist(mode="topic", topic="retrieval reranking", wiki_root=wiki, limit=5)

        self.assertEqual([candidate["title"] for candidate in payload["shortlist"]], ["Fresh Topic Paper"])
        self.assertEqual(payload["wiki_dedup_count"], 1)

    def test_specific_relevance_beats_generic_high_citation_hub(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = self._write_profile_wiki(Path(tmp))
            candidates = [
                {
                    "title": "GPT-4 Technical Report",
                    "paperId": "hub",
                    "abstract": "Large language models, neural generation, benchmark evaluation, and training.",
                    "citationCount": 100000,
                    "year": 2025,
                },
                {
                    "title": "Sparse Adapter Reranking for Retrieval Augmented Reasoning",
                    "paperId": "specific",
                    "abstract": "Adapter routing and retrieval reranking for grounded long-context reasoning with citation attribution.",
                    "citationCount": 8,
                    "year": 2025,
                },
            ]

            with mock.patch.object(discover, "_gather_from_topic", return_value=candidates):
                payload = discover.build_shortlist(mode="topic", topic="retrieval augmented reasoning", wiki_root=wiki, limit=2)

        self.assertEqual(payload["shortlist"][0]["title"], "Sparse Adapter Reranking for Retrieval Augmented Reasoning")

    def test_mocked_fixture_reduces_hub_intrusion_against_legacy_score(self) -> None:
        hub = {
            "title": "GPT-4 Technical Report",
            "paperId": "hub",
            "abstract": "Large language models, neural generation, benchmark evaluation, and training.",
            "citationCount": 100000,
            "year": 2025,
        }
        specific = {
            "title": "Sparse Adapter Reranking for Retrieval Augmented Reasoning",
            "paperId": "specific",
            "abstract": "Adapter routing and retrieval reranking for grounded long-context reasoning with citation attribution.",
            "citationCount": 8,
            "year": 2025,
        }
        legacy_hub = 0.45 * discover._influence_score(0, hub["citationCount"]) + 0.25 * discover._freshness_score(hub["year"])
        legacy_specific = 0.45 * discover._influence_score(0, specific["citationCount"]) + 0.25 * discover._freshness_score(specific["year"])
        self.assertGreater(legacy_hub, legacy_specific)

        with tempfile.TemporaryDirectory() as tmp:
            wiki = self._write_profile_wiki(Path(tmp))
            with mock.patch.object(discover, "_gather_from_topic", return_value=[hub, specific]):
                payload = discover.build_shortlist(mode="topic", topic="retrieval augmented reasoning", wiki_root=wiki, limit=2)

        self.assertEqual(payload["shortlist"][0]["paperId"], "specific")

    def test_sparse_wiki_fails_before_fetching(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            (wiki / "papers").mkdir(parents=True)
            with mock.patch.object(discover, "_fetch_papercopilot", side_effect=AssertionError("fetch called")):
                with self.assertRaisesRegex(ValueError, "Wiki too sparse"):
                    discover.build_shortlist(mode="venue", venue="neurips", year=2024, wiki_root=wiki)

    def test_venue_ranking_and_title_dedup_are_local(self) -> None:
        records = [
            {
                "id": "relevant",
                "title": "Efficient Retrieval Augmented Reasoning",
                "abstract": "Retrieval augmented generation with adapters, long context reasoning, and factual grounding.",
                "keywords": "retrieval; generation; adapters",
                "rating_avg": 8.0,
            },
            {
                "id": "offtopic",
                "title": "Dense Segmentation for Satellite Images",
                "abstract": "A computer vision system for remote sensing segmentation.",
                "keywords": "segmentation; remote sensing",
                "rating_avg": 9.0,
            },
            {
                "id": "duplicate",
                "title": "Existing Venue Paper",
                "abstract": "Retrieval augmented generation paper already present in the wiki.",
            },
        ]

        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            papers = wiki / "papers"
            concepts = wiki / "concepts"
            papers.mkdir(parents=True)
            concepts.mkdir(parents=True)
            (papers / "existing.md").write_text(
                "---\n"
                "title: Existing Venue Paper\n"
                "arxiv: 2401.99999v2\n"
                "---\n"
                "# Existing Venue Paper\n"
                "Retrieval augmented generation, adapters, long context, factual grounding, "
                "open domain question answering, citation attribution, reranking, chunking, "
                "knowledge intensive tasks, reasoning traces, vector search, dense retrieval.\n",
                encoding="utf-8",
            )
            (concepts / "rag.md").write_text(
                "# Retrieval Augmented Generation\n"
                "Adapters, grounding, reranking, long context reasoning, and dense retrieval "
                "are active topics in this wiki.\n",
                encoding="utf-8",
            )
            (papers / "unrelated.md").write_text(
                "---\n"
                "title: Unrelated Existing Paper\n"
                "arxiv: 2402.11111\n"
                "---\n"
                "# Unrelated Existing Paper\n"
                "This page is already in the wiki but is not in the venue candidate list.\n",
                encoding="utf-8",
            )

            with mock.patch.object(discover, "_fetch_papercopilot", return_value=records):
                payload = discover.build_shortlist(
                    mode="venue",
                    venue="neurips",
                    year=2024,
                    wiki_root=wiki,
                    limit=5,
                )

            titles = [candidate["title"] for candidate in payload["shortlist"]]
            self.assertNotIn("Existing Venue Paper", titles)
            self.assertEqual(titles[0], "Efficient Retrieval Augmented Reasoning")
            self.assertEqual(payload["wiki_dedup_count"], 1)
            self.assertFalse((wiki / "log.md").exists())
            self.assertFalse((Path(tmp) / "raw").exists())

    def test_venue_semantic_boost_matches_papercopilot_candidate(self) -> None:
        records = [
            {
                "id": "semantic",
                "title": "Sparse Adapter Reranking for Retrieval Augmented Reasoning",
                "abstract": "A short abstract with little lexical evidence.",
                "rating_avg": 5.0,
            },
            {
                "id": "metadata",
                "title": "Generic Neural Language Model Evaluation",
                "abstract": "Language model benchmark evaluation and training.",
                "rating_avg": 9.5,
                "gs_citation": "5000",
            },
        ]
        s2_hits = [
            {
                "paperId": "s2-semantic",
                "title": "Sparse Adapter Reranking for Retrieval Augmented Reasoning",
                "abstract": "retrieval reranking adapter routing",
                "externalIds": {"ArXiv": "2405.12345"},
                "citationCount": 3,
                "score": 0.93,
            }
        ]

        with tempfile.TemporaryDirectory() as tmp:
            wiki = self._write_profile_wiki(Path(tmp))
            with (
                mock.patch.object(discover, "_fetch_papercopilot", return_value=records),
                mock.patch.object(discover.fetch_s2, "S2_API_KEY", "test-key"),
                mock.patch.object(discover.fetch_s2, "search", return_value=s2_hits),
            ):
                payload = discover.build_shortlist(
                    mode="venue",
                    venue="neurips",
                    year=2024,
                    wiki_root=wiki,
                    limit=2,
                )

        self.assertEqual(payload["shortlist"][0]["title"], "Sparse Adapter Reranking for Retrieval Augmented Reasoning")
        self.assertGreater(payload["shortlist"][0].get("_semantic_match_score", 0), 0)

    def test_venue_relevance_guard_runs_after_wiki_dedup(self) -> None:
        records = [
            {
                "id": "duplicate",
                "title": "Existing Venue Paper",
                "abstract": "Retrieval augmented generation paper already present in the wiki.",
            },
            {
                "id": "offtopic",
                "title": "Catalyst Geometry for Battery Electrolytes",
                "abstract": "Polymer conductivity, lithium cathodes, anodes, and electrochemical cells.",
                "rating_avg": 9.0,
            },
        ]

        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            papers = wiki / "papers"
            concepts = wiki / "concepts"
            papers.mkdir(parents=True)
            concepts.mkdir(parents=True)
            (papers / "existing.md").write_text(
                "---\n"
                "title: Existing Venue Paper\n"
                "---\n"
                "# Existing Venue Paper\n"
                "Retrieval augmented generation, adapters, long context, factual grounding, "
                "open domain question answering, citation attribution, reranking, chunking, "
                "knowledge intensive tasks, reasoning traces, vector search, dense retrieval.\n",
                encoding="utf-8",
            )
            (concepts / "rag.md").write_text(
                "# Retrieval Augmented Generation\n"
                "Adapters, grounding, reranking, long context reasoning, dense retrieval, "
                "faithfulness, query rewriting, answer synthesis, attribution, knowledge editing.\n",
                encoding="utf-8",
            )

            with mock.patch.object(discover, "_fetch_papercopilot", return_value=records):
                with self.assertRaisesRegex(ValueError, "after filtering existing wiki papers"):
                    discover.build_shortlist(
                        mode="venue",
                        venue="neurips",
                        year=2024,
                        wiki_root=wiki,
                        limit=5,
                    )

    def test_from_venue_help_omits_anchor_only_limit(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "discover.py"), "from-venue", "--help"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertNotIn("--per-anchor-limit", proc.stdout)

    def test_from_venue_sparse_cli_fails_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            wiki = Path(tmp) / "wiki"
            (wiki / "papers").mkdir(parents=True)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(TOOLS / "discover.py"),
                    "from-venue",
                    "--venue",
                    "neurips",
                    "--year",
                    "2024",
                    "--wiki-root",
                    str(wiki),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Wiki too sparse", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()

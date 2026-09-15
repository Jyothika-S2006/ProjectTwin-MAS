import re
import math
from collections import Counter
from typing import List, Dict, Any, Tuple
from rapidfuzz import fuzz
from core.models import RawExecutionEvent, CandidateMatch, BaselineActivity

class PureTfidfVectorizer:
    """Pure-Python character n-gram TF-IDF vectorizer and cosine calculator."""
    def __init__(self, ngram_range=(2, 4)):
        self.ngram_range = ngram_range
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    def _get_ngrams(self, text: str) -> List[str]:
        cleaned = f" {text.lower().strip()} "
        ngrams = []
        n_min, n_max = self.ngram_range
        for n in range(n_min, n_max + 1):
            for i in range(len(cleaned) - n + 1):
                ngrams.append(cleaned[i:i+n])
        return ngrams

    def fit(self, documents: List[str]):
        doc_freq = Counter()
        N = len(documents)
        for doc in documents:
            unique_ngrams = set(self._get_ngrams(doc))
            for ng in unique_ngrams:
                doc_freq[ng] += 1
        self.vocab = {ng: idx for idx, (ng, _) in enumerate(doc_freq.most_common(5000))}
        self.idf = {ng: math.log((1 + N) / (1 + count)) + 1.0 for ng, count in doc_freq.items()}

    def transform_one(self, text: str) -> Dict[str, float]:
        ngrams = self._get_ngrams(text)
        counts = Counter(ngrams)
        vec = {}
        for ng, count in counts.items():
            if ng in self.idf:
                tf = 1.0 + math.log(count)
                vec[ng] = tf * self.idf[ng]
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {k: v / norm for k, v in vec.items()}

    def cosine_sim(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        dot = sum(val * vec2.get(k, 0.0) for k, val in vec1.items())
        return max(0.0, min(1.0, dot))


class HybridLinkingAgent:
    """
    Hybrid Terminology & Schedule Linking Agent.
    Combines:
      1. RapidFuzz (Token Sort, Token Set, Partial Ratio)
      2. BM25 / Domain Keyword Retrieval
      3. Character n-gram TF-IDF Cosine Similarity
      4. Engineering Metadata Boosting (Tags, Lines, Disciplines)
    """
    def __init__(self, baseline_activities: Dict[str, BaselineActivity]):
        self.baseline_activities = baseline_activities
        self.activity_ids = list(baseline_activities.keys())
        self.activity_corpus = [
            f"{act.activity_name} {act.discipline} {act.unit_area} {act.wbs_code}"
            for act in baseline_activities.values()
        ]
        self.vectorizer = PureTfidfVectorizer(ngram_range=(3, 5))
        if self.activity_corpus:
            self.vectorizer.fit(self.activity_corpus)
            self.doc_vectors = [self.vectorizer.transform_one(doc) for doc in self.activity_corpus]
        else:
            self.doc_vectors = []

    def _extract_engineering_tags(self, text: str) -> List[str]:
        """Extracts equipment IDs, line codes, rack numbers, pad tags."""
        patterns = [
            r"\b[0-9]{2}-[A-Z]{2,4}-[0-9]{3}\b",  # e.g. 24-CW-001, 16-DIS-002
            r"\bP-[0-9]{2}[A-B]?\b",              # e.g. P-12, P-101A
            r"\bTK-[0-9]{3}\b",                    # e.g. TK-101
            r"\bPR-[0-9]{2}\b",                    # e.g. PR-04
            r"\bMCC-[0-9]{2}\b",                   # e.g. MCC-01
            r"\bC-[0-9]\b",                        # e.g. C-1
            r"\bFT-[0-9]{3}\b",                    # e.g. FT-101
            r"\bPT-[0-9]{3}\b",                    # e.g. PT-204
            r"\bGJ-[0-9]{2}\b",                    # e.g. GJ-04
            r"\b11kV\b",                           # 11kV
            r"\bM35\b",                            # M35
        ]
        found = []
        for pat in patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            found.extend([m.upper() for m in matches])
        return list(set(found))

    def link_event(self, event: RawExecutionEvent, top_k: int = 3) -> List[CandidateMatch]:
        """
        Takes a RawExecutionEvent and returns top-K ranked L5/L6 candidate activities with transparent breakdown.
        """
        query_text = f"{event.extracted_activity} {event.raw_text}".strip()
        query_tags = self._extract_engineering_tags(query_text)
        query_discipline = event.discipline

        q_vec = self.vectorizer.transform_one(query_text) if self.doc_vectors else {}

        candidates = []

        for idx, act_id in enumerate(self.activity_ids):
            act = self.baseline_activities[act_id]
            target_str = f"{act.activity_name} {act.unit_area}".lower()
            q_lower = query_text.lower()

            # 1. RapidFuzz Syntactic Matching
            token_sort = fuzz.token_sort_ratio(q_lower, target_str) / 100.0
            token_set = fuzz.token_set_ratio(q_lower, target_str) / 100.0
            partial = fuzz.partial_ratio(q_lower, target_str) / 100.0
            fuzzy_score = (token_sort * 0.4) + (token_set * 0.4) + (partial * 0.2)

            # 2. BM25 / Keyword Retrieval Approximation
            act_tokens = set(re.findall(r"\w+", target_str))
            query_tokens = set(re.findall(r"\w+", q_lower))
            overlap = act_tokens.intersection(query_tokens)
            bm25_score = min(1.0, len(overlap) / max(1, len(act_tokens) ** 0.6))

            # 3. Semantic Cosine Score from n-gram TF-IDF
            semantic_score = self.vectorizer.cosine_sim(q_vec, self.doc_vectors[idx]) if idx < len(self.doc_vectors) else 0.0

            # 4. Domain Metadata Boosting
            boost = 0.0
            rationale_parts = []

            # Discipline alignment
            if query_discipline and act.discipline:
                if query_discipline.lower() == act.discipline.lower():
                    boost += 0.15
                    rationale_parts.append(f"Discipline '{act.discipline}' matched (+15%)")
                elif query_discipline.lower() in ["piping", "mechanical"] and act.discipline.lower() in ["piping", "mechanical"]:
                    boost += 0.08
                    rationale_parts.append(f"Inter-discipline '{act.discipline}' related (+8%)")

            # Engineering Code / Tag alignment
            act_tags = self._extract_engineering_tags(act.activity_name + " " + act.unit_area)
            matched_tags = set(query_tags).intersection(set(act_tags))
            if matched_tags:
                boost += 0.25
                rationale_parts.append(f"Direct equipment/line tag match: {', '.join(matched_tags)} (+25%)")

            # Composite confidence (0 - 100)
            base_score = (fuzzy_score * 0.35) + (bm25_score * 0.30) + (semantic_score * 0.35)
            composite_score = min(99.0, (base_score * (1.0 + boost)) * 100.0)

            # Formulate rationale
            if not rationale_parts:
                rationale_parts.append(f"Lexical token overlap: {', '.join(list(overlap)[:3]) if overlap else 'General match'}")

            full_rationale = f"Confidence {composite_score:.1f}%: " + "; ".join(rationale_parts)

            candidates.append(CandidateMatch(
                activity_id=act.activity_id,
                activity_name=act.activity_name,
                discipline=act.discipline,
                wbs_code=act.wbs_code,
                fuzzy_score=round(fuzzy_score * 100, 1),
                bm25_score=round(bm25_score * 100, 1),
                semantic_score=round(semantic_score * 100, 1),
                domain_boost=round(boost * 100, 1),
                composite_confidence=round(composite_score, 1),
                match_rationale=full_rationale
            ))

        # Rank candidates by composite confidence descending
        candidates.sort(key=lambda x: x.composite_confidence, reverse=True)
        return candidates[:top_k]

import re
from difflib import SequenceMatcher
from typing import Optional
from modules.logger import get_logger, trace

log = get_logger(__name__)

# =====================================================================
# MATCHING CONFIGURATION
# =====================================================================

# Minimum similarity score (0.0 – 1.0) to qualify as a candidate match
DEFAULT_SCORE_THRESHOLD = 0.45

# Field weights used when computing the composite match score
FIELD_WEIGHTS = {
    "name":        0.40,   # Item name is the strongest signal
    "description": 0.35,   # Description carries rich semantic content
    "category":    0.25,   # Category is a hard structural filter helper
}

# Common filler words to strip before comparison (improves token overlap)
_STOP_WORDS = {
    "a", "an", "the", "my", "is", "it", "of", "in", "on", "at",
    "and", "or", "with", "i", "lost", "found", "item"
}


# =====================================================================
# TEXT NORMALIZATION HELPERS
# =====================================================================

def _normalize(text: str) -> str:
    """
    Lowercases, strips punctuation, and removes stop words from a string.
    Returns a cleaned string ready for similarity comparison.

    Args:
        text: Raw input string (name, description, etc.)

    Returns:
        Normalized string with stop words removed.
    """
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)          # Remove punctuation
    tokens = [t for t in text.split() if t not in _STOP_WORDS]
    return " ".join(tokens)


def _token_overlap_score(a: str, b: str) -> float:
    """
    Computes a Jaccard-like token overlap ratio between two strings.
    Complements SequenceMatcher by rewarding shared keyword presence
    regardless of order.

    Args:
        a: First normalized string.
        b: Second normalized string.

    Returns:
        Float in [0.0, 1.0] representing token overlap.
    """
    tokens_a = set(a.split())
    tokens_b = set(b.split())
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def _sequence_similarity(a: str, b: str) -> float:
    """
    Uses Python's SequenceMatcher to compute character-level similarity.

    Args:
        a: First string.
        b: Second string.

    Returns:
        Float in [0.0, 1.0].
    """
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def _field_similarity(raw_a: str, raw_b: str) -> float:
    """
    Combines sequence similarity and token overlap into a single field score.
    Uses a 60/40 blend: sequence ratio captures structure, token overlap
    captures keyword presence.

    Args:
        raw_a: Raw value from the first item's field.
        raw_b: Raw value from the second item's field.

    Returns:
        Blended float score in [0.0, 1.0].
    """
    a = _normalize(raw_a)
    b = _normalize(raw_b)
    seq_score   = _sequence_similarity(a, b)
    token_score = _token_overlap_score(a, b)
    return round(0.60 * seq_score + 0.40 * token_score, 4)


# =====================================================================
# CORE MATCHING UTILITY
# =====================================================================

@trace
def compute_match_score(lost_item: dict, found_item: dict) -> float:
    """
    Computes a weighted composite similarity score between a Lost item
    and a Found item using their name, description, and category.

    Hard filter: items from different categories score 0.0 immediately,
    unless either category is None/missing (treated as unknown → not filtered).

    Args:
        lost_item:  Dict with keys: 'name', 'description', 'category_name' (or 'category_id').
        found_item: Dict with keys: 'name', 'description', 'category_name' (or 'category_id').

    Returns:
        Composite score float in [0.0, 1.0].
        Higher = stronger match candidate.

    Example:
        score = compute_match_score(lost, found)
        if score >= 0.5:
            print("Potential match found!")
    """
    # --- Hard category filter ---
    lost_cat  = lost_item.get("category_name") or lost_item.get("category_id")
    found_cat = found_item.get("category_name") or found_item.get("category_id")

    if lost_cat and found_cat and lost_cat != found_cat:
        log.debug(f"Category mismatch ({lost_cat} ≠ {found_cat}) — score forced to 0.0")
        return 0.0

    # --- Field scores ---
    name_score  = _field_similarity(
        lost_item.get("name", ""),
        found_item.get("name", "")
    )
    desc_score  = _field_similarity(
        lost_item.get("description", ""),
        found_item.get("description", "")
    )
    # Category contributed implicitly via the hard filter above; use 1.0 if same
    cat_score   = 1.0 if (lost_cat and found_cat and lost_cat == found_cat) else 0.5

    composite = (
        FIELD_WEIGHTS["name"]        * name_score  +
        FIELD_WEIGHTS["description"] * desc_score  +
        FIELD_WEIGHTS["category"]    * cat_score
    )

    log.debug(
        f"Match score: name={name_score:.2f} desc={desc_score:.2f} "
        f"cat={cat_score:.2f} → composite={composite:.4f}"
    )
    return round(composite, 4)


# =====================================================================
# HIGH-LEVEL MATCHING HELPERS
# =====================================================================

@trace
def find_matches_for_item(
    target_item: dict,
    candidate_items: list[dict],
    threshold: float = DEFAULT_SCORE_THRESHOLD
) -> list[dict]:
    """
    Given one item (lost or found), returns all candidates that score
    at or above the threshold, sorted by score descending.

    Intended to be called by a presenter after fetching items from queries.py.

    Args:
        target_item:     The item to match against (dict from get_item_details).
        candidate_items: List of items to compare against (dicts from search_active_items).
        threshold:       Minimum score to include in results (default: 0.45).

    Returns:
        List of dicts, each being the candidate item dict with an added
        'match_score' key, sorted highest-score-first.

    Example:
        lost = get_item_details(item_id=5, item_type='Lost')
        candidates = search_active_items(item_type='Found')
        matches = find_matches_for_item(lost, candidates)
    """
    results = []

    for candidate in candidate_items:
        # Skip self-comparison if same item_id is present
        if candidate.get("item_id") == target_item.get("item_id"):
            continue

        score = compute_match_score(target_item, candidate)

        if score >= threshold:
            enriched = dict(candidate)
            enriched["match_score"] = score
            results.append(enriched)

    results.sort(key=lambda x: x["match_score"], reverse=True)
    log.info(
        f"Matching complete for item_id={target_item.get('item_id')} — "
        f"{len(results)} candidate(s) found above threshold {threshold}."
    )
    return results


def is_likely_match(lost_item: dict, found_item: dict,
                    threshold: float = DEFAULT_SCORE_THRESHOLD) -> bool:
    """
    Convenience boolean helper. Returns True if the pair scores above threshold.

    Args:
        lost_item:  Lost item dict.
        found_item: Found item dict.
        threshold:  Score cutoff (default: 0.45).

    Returns:
        True if likely a match, False otherwise.

    Example:
        if is_likely_match(lost, found):
            notify_constituent(...)
    """
    return compute_match_score(lost_item, found_item) >= threshold


def get_best_match(
    target_item: dict,
    candidate_items: list[dict],
    threshold: float = DEFAULT_SCORE_THRESHOLD
) -> Optional[dict]:
    """
    Returns only the single best-scoring candidate, or None if no candidate
    meets the threshold. Useful for quick single-match lookups.

    Args:
        target_item:     Item to find a match for.
        candidate_items: Pool of items to search.
        threshold:       Minimum qualifying score.

    Returns:
        The best-match candidate dict (with 'match_score' key), or None.
    """
    matches = find_matches_for_item(target_item, candidate_items, threshold)
    return matches[0] if matches else None


# =====================================================================
# BATCH MATCHING UTILITY
# =====================================================================

@trace
def batch_match_all(
    lost_items: list[dict],
    found_items: list[dict],
    threshold: float = DEFAULT_SCORE_THRESHOLD
) -> list[dict]:
    """
    Runs matching across every lost item against every found item.
    Returns a flat list of all qualifying pairs, sorted by score descending.
    Designed for dashboard-level overview or background matching tasks.

    Args:
        lost_items:  List of lost item dicts.
        found_items: List of found item dicts.
        threshold:   Minimum score to include (default: 0.45).

    Returns:
        List of match-pair dicts:
        [
            {
                "lost_item_id":   int,
                "lost_name":      str,
                "found_item_id":  int,
                "found_name":     str,
                "match_score":    float
            },
            ...
        ]
    """
    pairs = []

    for lost in lost_items:
        for found in found_items:
            score = compute_match_score(lost, found)
            if score >= threshold:
                pairs.append({
                    "lost_item_id":  lost.get("item_id"),
                    "lost_name":     lost.get("name", ""),
                    "found_item_id": found.get("item_id"),
                    "found_name":    found.get("name", ""),
                    "match_score":   score
                })

    pairs.sort(key=lambda x: x["match_score"], reverse=True)
    log.info(f"Batch match complete — {len(pairs)} pair(s) found across "
             f"{len(lost_items)} lost × {len(found_items)} found items.")
    return pairs


# =====================================================================
# MODULE SELF-TEST
# =====================================================================

if __name__ == "__main__":
    # Sample items for smoke testing
    sample_lost = {
        "item_id": 1,
        "name": "Black Wireless Earphones",
        "description": "Sony WH-1000XM4, black color, left earcup has scratch",
        "category_name": "Electronics"
    }
    sample_found_a = {
        "item_id": 2,
        "name": "Wireless Earphones Black",
        "description": "Found black Sony earphones near the library, scratched earcup",
        "category_name": "Electronics"
    }
    sample_found_b = {
        "item_id": 3,
        "name": "Blue Umbrella",
        "description": "Small foldable blue umbrella with wooden handle",
        "category_name": "Clothing & Accessories"
    }

    print("=== Matching Self-Test ===\n")

    score_a = compute_match_score(sample_lost, sample_found_a)
    score_b = compute_match_score(sample_lost, sample_found_b)
    print(f"Lost ↔ Found A score : {score_a}  (expect HIGH)")
    print(f"Lost ↔ Found B score : {score_b}  (expect LOW / 0.0)\n")

    results = find_matches_for_item(sample_lost, [sample_found_a, sample_found_b])
    print(f"Candidates above threshold: {len(results)}")
    for r in results:
        print(f"  → item_id={r['item_id']} | {r['name']} | score={r['match_score']}")

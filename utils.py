"""Hashing helpers used by the blockchain simulation."""
import hashlib
import json
from typing import Any, Iterable


def calculate_hash(data: Any) -> str:
    """Return a deterministic SHA-256 hex digest for data."""
    if isinstance(data, (dict, list)):
        payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    else:
        payload = str(data)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get_merkle_root(transactions: Iterable[dict]) -> str:
    """Calculate a Merkle root, duplicating the last leaf on odd levels."""
    hashes = [calculate_hash(transaction) for transaction in transactions]
    if not hashes:
        return calculate_hash("")
    while len(hashes) > 1:
        if len(hashes) % 2:
            hashes.append(hashes[-1])
        hashes = [calculate_hash(hashes[i] + hashes[i + 1]) for i in range(0, len(hashes), 2)]
    return hashes[0]


def build_block_header(index: int, timestamp: float, merkle_root: str,
                       previous_hash: str, difficulty: int) -> str:
    """Serialize immutable block-header fields for proof-of-work."""
    return json.dumps({
        "difficulty": difficulty, "index": index, "merkle_root": merkle_root,
        "previous_hash": previous_hash, "timestamp": timestamp,
    }, sort_keys=True, separators=(",", ":"))

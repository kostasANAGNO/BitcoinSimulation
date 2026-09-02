"""Block model and proof-of-work validation."""
from dataclasses import dataclass, field
from utils import build_block_header, calculate_hash, get_merkle_root


@dataclass
class Block:
    index: int
    timestamp: float
    transactions: list[dict]
    previous_hash: str
    difficulty: int
    nonce: int
    merkle_root: str = field(init=False)
    hash: str = field(init=False)

    def __post_init__(self) -> None:
        self.transactions = [transaction.copy() for transaction in self.transactions]
        self.merkle_root = get_merkle_root(self.transactions)
        self.hash = self.compute_hash()

    def header(self) -> str:
        return build_block_header(self.index, self.timestamp, self.merkle_root,
                                  self.previous_hash, self.difficulty)

    def compute_hash(self) -> str:
        return calculate_hash(self.header() + str(self.nonce))

    def has_valid_proof(self) -> bool:
        return self.hash == self.compute_hash() and self.hash.startswith("0" * self.difficulty)

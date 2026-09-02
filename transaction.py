"""Transaction model for the simulation."""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Transaction:
    sender: str
    recipient: str
    amount: float

    def __post_init__(self) -> None:
        if not self.sender or not self.recipient:
            raise ValueError("Sender and recipient must not be empty")
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")

    def to_dict(self) -> dict:
        return asdict(self)

import unittest
from blockchain import Blockchain
from transaction import Transaction
from utils import calculate_hash, get_merkle_root


class UtilityTests(unittest.TestCase):
    def test_hash_is_deterministic_for_dicts(self):
        self.assertEqual(calculate_hash({"b": 2, "a": 1}), calculate_hash({"a": 1, "b": 2}))

    def test_merkle_root_handles_empty_and_odd_lists(self):
        self.assertEqual(get_merkle_root([]), calculate_hash(""))
        self.assertEqual(len(get_merkle_root([{"id": 1}, {"id": 2}, {"id": 3}])), 64)


class TransactionTests(unittest.TestCase):
    def test_rejects_non_positive_amount(self):
        with self.assertRaises(ValueError):
            Transaction("Alice", "Bob", 0)


class BlockchainTests(unittest.TestCase):
    def test_mines_and_validates_block(self):
        chain = Blockchain(difficulty=1, adjustment_interval=10, verbose=False)
        chain.add_transaction("Alice", "Bob", 10)
        self.assertIsNotNone(chain.start_mining_race())
        self.assertEqual(len(chain.chain), 2)
        self.assertTrue(chain.is_chain_valid())

    def test_detects_tampering(self):
        chain = Blockchain(difficulty=1, adjustment_interval=10, verbose=False)
        chain.add_transaction("Alice", "Bob", 10)
        chain.start_mining_race()
        chain.chain[1].transactions[0]["amount"] = 999
        self.assertFalse(chain.is_chain_valid())


if __name__ == "__main__":
    unittest.main()

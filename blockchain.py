"""Core blockchain orchestration and consensus logic."""
import queue
import random
import time
from multiprocessing import Event, Lock, Queue, Value
from block import Block
from miner import Miner
from transaction import Transaction
from utils import build_block_header, get_merkle_root


class Blockchain:
    def __init__(self, difficulty=4, target_block_time=3.0, adjustment_interval=5,
                 miner_count=3, consensus_timeout=120.0, verbose=True):
        if difficulty < 1 or adjustment_interval < 1 or miner_count < 2:
            raise ValueError("Difficulty and interval must be positive; use at least 2 miners")
        self.chain = []
        self.pending_transactions = []
        self.difficulty = difficulty
        self.target_block_time = target_block_time
        self.adjustment_interval = adjustment_interval
        self.miner_count = miner_count
        self.consensus_timeout = consensus_timeout
        self.verbose = verbose
        self.create_genesis_block()

    def _log(self, message):
        if self.verbose:
            print(message)

    def create_genesis_block(self):
        self._log("--- Genesis Block Created ---")
        self.chain.append(Block(0, time.time() - self.target_block_time, [], "0", 0, 0))

    def add_transaction(self, sender, recipient, amount):
        self.pending_transactions.append(Transaction(sender, recipient, amount).to_dict())

    def adjust_difficulty(self):
        mined_blocks = len(self.chain) - 1
        if mined_blocks == 0 or mined_blocks % self.adjustment_interval:
            return
        durations = [self.chain[-i].timestamp - self.chain[-i - 1].timestamp
                     for i in range(1, self.adjustment_interval + 1)]
        average = sum(durations) / len(durations)
        self._log(f"Average over {self.adjustment_interval} blocks: {average:.4f}s "
                  f"(target {self.target_block_time:.4f}s)")
        if average < self.target_block_time / 2:
            self.difficulty += 1
            self._log(f"Mining was fast; difficulty increased to {self.difficulty}")
        elif average > self.target_block_time * 2 and self.difficulty > 1:
            self.difficulty -= 1
            self._log(f"Mining was slow; difficulty decreased to {self.difficulty}")

    def start_mining_race(self):
        if not self.pending_transactions:
            return None
        last_block = self.chain[-1]
        timestamp = time.time()
        index = len(self.chain)
        transactions = [transaction.copy() for transaction in self.pending_transactions]
        block_header = build_block_header(index, timestamp, get_merkle_root(transactions),
                                          last_block.hash, self.difficulty)
        found_event, winner_lock, vote_queue = Event(), Lock(), Queue()
        solution_nonce = Value("Q", 0)
        miners = [Miner(f"Miner_{n}", found_event, solution_nonce, winner_lock,
                        vote_queue, block_header, self.difficulty,
                        random.uniform(0, 0.002))
                  for n in range(1, self.miner_count + 1)]
        self._log(f"Mining started | difficulty: {self.difficulty}")
        for miner in miners:
            miner.start()

        winner, valid_votes = None, 0
        deadline = time.monotonic() + self.consensus_timeout
        try:
            for _ in miners:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("Consensus timed out")
                sender, message_type, data = vote_queue.get(timeout=remaining)
                if message_type == "WINNER":
                    winner = (sender, data[0])
                    self._log(f"{sender} found nonce {data[0]} ({data[1]})")
                elif message_type == "VALID":
                    valid_votes += 1
            if winner is None or valid_votes != self.miner_count - 1:
                self._log("Block rejected: consensus failed")
                return None
            block = Block(index, timestamp, transactions, last_block.hash,
                          self.difficulty, winner[1])
            if not block.has_valid_proof():
                self._log("Block rejected: invalid proof")
                return None
            self.chain.append(block)
            self.pending_transactions.clear()
            self._log(f"Consensus reached; block {block.index} accepted")
            self.adjust_difficulty()
            return block
        except queue.Empty as error:
            raise TimeoutError("Consensus timed out") from error
        finally:
            found_event.set()
            for miner in miners:
                miner.join(timeout=2)
                if miner.is_alive():
                    miner.terminate()
                    miner.join()
            vote_queue.close()

    def is_chain_valid(self):
        for index, block in enumerate(self.chain):
            if block.merkle_root != get_merkle_root(block.transactions):
                return False
            if block.hash != block.compute_hash():
                return False
            if index == 0:
                if block.previous_hash != "0":
                    return False
                continue
            if block.previous_hash != self.chain[index - 1].hash or not block.has_valid_proof():
                return False
        return True

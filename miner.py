"""Multiprocessing proof-of-work miner."""
import random
import time
from multiprocessing import Process
from utils import calculate_hash


class Miner(Process):
    def __init__(self, name, found_event, solution_nonce, winner_lock, vote_queue,
                 block_header, difficulty, simulated_delay=0.0):
        super().__init__(name=name)
        self.found_event = found_event
        self.solution_nonce = solution_nonce
        self.winner_lock = winner_lock
        self.vote_queue = vote_queue
        self.block_header = block_header
        self.difficulty = difficulty
        self.simulated_delay = simulated_delay

    def run(self):
        target = "0" * self.difficulty
        attempts = 0
        while not self.found_event.is_set():
            nonce = random.randrange(0, 2**63)
            candidate_hash = calculate_hash(self.block_header + str(nonce))
            if candidate_hash.startswith(target):
                with self.winner_lock:
                    if not self.found_event.is_set():
                        self.solution_nonce.value = nonce
                        self.found_event.set()
                        self.vote_queue.put((self.name, "WINNER", (nonce, candidate_hash)))
                        return
                break
            attempts += 1
            if attempts % 2_000 == 0 and self.simulated_delay:
                time.sleep(self.simulated_delay)

        nonce = self.solution_nonce.value
        candidate_hash = calculate_hash(self.block_header + str(nonce))
        vote = "VALID" if candidate_hash.startswith(target) else "INVALID"
        self.vote_queue.put((self.name, vote, None))

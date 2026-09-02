"""Command-line entry point for the blockchain simulation."""
import argparse
import time
from blockchain import Blockchain


def parse_args():
    parser = argparse.ArgumentParser(description="Run a multiprocessing blockchain demo")
    parser.add_argument("--blocks", type=int, default=6, help="number of blocks to mine")
    parser.add_argument("--difficulty", type=int, default=4, help="initial PoW difficulty")
    parser.add_argument("--pause", type=float, default=0.25, help="pause between blocks")
    return parser.parse_args()


def main():
    args = parse_args()
    blockchain = Blockchain(difficulty=args.difficulty)
    print("\n=== MULTIPROCESSING BLOCKCHAIN SIMULATION ===")
    for index in range(1, args.blocks + 1):
        print(f"\nBLOCK #{index}")
        blockchain.add_transaction("Alice", "Bob", index * 10)
        blockchain.add_transaction("Charlie", "Dave", index * 5)
        blockchain.start_mining_race()
        time.sleep(args.pause)
    print("\n=== CHAIN SUMMARY ===")
    for block in blockchain.chain:
        print(f"Block {block.index}: transactions={len(block.transactions)} | "
              f"difficulty={block.difficulty} | hash={block.hash[:16]}...")
    print(f"Chain valid: {blockchain.is_chain_valid()}")


if __name__ == "__main__":
    main()

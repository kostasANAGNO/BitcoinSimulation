# Multiprocessing Blockchain Simulation

An educational blockchain simulation written in Python. Multiple miner processes
race to solve a proof-of-work challenge, while the remaining miners validate the
winning nonce before the block is accepted.

> This project demonstrates blockchain concepts; it is not a cryptocurrency and
> must not be used for real financial transactions.

## Features

- SHA-256 block hashing
- Deterministic transaction hashing and Merkle roots
- Proof-of-work mining with configurable difficulty
- Multiprocessing miner race and consensus simulation
- Automatic difficulty adjustment
- Full-chain integrity validation
- Unit tests using Python's standard library

## Requirements

- Python 3.10 or newer
- No third-party runtime dependencies

## Run the demo

```bash
python main.py
```

Optional arguments:

```bash
python main.py --blocks 3 --difficulty 3 --pause 0.1
```

Higher difficulty values can increase mining time substantially.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Project structure

```text
.
|-- block.py          # Block model and proof validation
|-- blockchain.py     # Chain, mining orchestration, and consensus
|-- main.py           # Command-line demo
|-- miner.py          # Multiprocessing miner
|-- transaction.py    # Validated transaction model
|-- utils.py          # SHA-256 and Merkle-tree helpers
`-- tests/            # Unit tests
```

## How it works

Each block commits to its index, timestamp, Merkle root, previous block hash,
and difficulty. Miner processes generate nonces until one produces a SHA-256
hash with the required number of leading zeroes. The other miners independently
verify that nonce. Once consensus is reached, the block is appended to the chain.

Difficulty is reviewed after a configurable number of blocks and moves by one
level when mining is much faster or slower than the target block interval.

## Limitations

This intentionally simplified model has no wallets, signatures, balances,
persistent storage, peer-to-peer networking, or adversarial consensus rules.

## License

Released under the [MIT License](LICENSE).

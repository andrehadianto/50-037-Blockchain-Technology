from Block import Block
import time
import hashlib
import cbor
import random


class Blockchain:
    TARGET = {
        1: b'\xff' * 256,
        2: b'\x11' + b'\xff' * 255,
        3: b'\x00' * 3 + b'\xff' * 253
    }

    def __init__(self):
        self.difficulty = 3
        self.blockchain_graph = {}
        self.longest_chain = []
        self.longest_header = None

        self.generate_genesis_block()

    def generate_genesis_block(self):
        """
        generating the genesis block
        """
        genesis_block = Block([], "i am genesis", None)
        while True:
            nonce = str(random.randint(0, 300000))
            genesis_block.set_nonce(nonce)
            to_hash = genesis_block.serialize()
            digest = hashlib.sha256(to_hash).hexdigest()
            if self.verify_pow(digest):
                break
        self.blockchain_graph[digest] = {
            "children": [],
            "height": 0,
            "block": genesis_block,
            "balance_map": {}
        }
        self.longest_header = digest

    def verify_pow(self, digest):
        if self.difficulty < 1:
            self.difficulty = 1
        if self.difficulty > 3:
            self.difficulty = 3
        if digest < Blockchain.TARGET[self.difficulty].hex():
            return True
        return False

    def validate_block(self, block):
        """
        ensure proof of work is valid, transactions are new, timestamp
        return block isValidated
        """
        to_hash = block.serialize()
        digest = hashlib.sha256(to_hash).hexdigest()
        if not self.verify_pow(digest):
            return False
        elif block.get_header()["timestamp"] < self.blockchain_graph[self.longest_header]["block"].get_header()["timestamp"]:
            return False
        for trans in block.merkle_tree.past_transactions:
            for digest in self.longest_chain:
                if trans in self.blockchain_graph[digest]["block"].merkle_tree.past_transactions:
                    return False
        return True

    def add_block(self, block):
        if self.validate_block(block):
            pass

    def create_longest_chain(self, longest_header):
        longest_chain = []
        while True:
            parent = self.blockchain_graph[longest_header]["block"].get_header()[
                "prev_header"]
            pass

    def update_longest_header(self):
        pass

    def resolve(self):
        """
        get longest header and compute the longest chain through recurrence
        return longest chain through recurrence
        """
        pass


if __name__ == "__main__":
    bc = Blockchain()
    print(bc.blockchain_graph)
    print(bc.longest_header)

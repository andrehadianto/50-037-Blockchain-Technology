from MerkleTree import MerkleTree
import cbor
import time
import random
import hashlib


class Block:
    def __init__(self, transactions, prev_header, miner_id):
        self.merkle_tree = MerkleTree()
        for trans in transactions:
            self.merkle_tree.add(trans)
        self.merkle_tree.build()
        self.miner_id = miner_id
        self.header = {
            "timestamp": None,
            "root": None,
            "nonce": None,
            "prev_header": None
        }
        self.header["timestamp"] = int(time.time())
        self.header["root"] = self.merkle_tree.get_root()
        self.header["prev_header"] = prev_header

    def serialize(self):
        return json.dumps(self.header)

    def set_nonce(self, nonce):
        self.header[nonce] = nonce

    def get_header(self):
        return self.header

    def hash_header(self):
        to_hash = self.serialize()
        digest = hashlib.sha256(to_hash).hexdigest()
        return digest

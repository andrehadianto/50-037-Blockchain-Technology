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
        ## CHECK INCOMING BLOCK IS MINED AFTER THE PARENT BLOCK ##
        elif block.get_header()["timestamp"] < self.blockchain_graph[block.get_header()["prev_header"]]["block"].get_header()["timestamp"]:
            return False
        ## CHECK FOR DUPLICATE TRANSACTIONS ##
        for trans in block.merkle_tree.past_transactions:
            for block_ in self.create_chain_to_parent_block(block): # transactions from the added block's parent all the way to the genesis.
                if trans in block_.merkle_tree.past_transactions:
                    return False
        return True

    def add_block(self, block):
        if self.validate_block(block):
            digest = block.hash_header()
            prev_level = self.blockchain_graph[block.get_header()["prev_header"]]["height"]
            self.blockchain_graph[block.get_header()["prev_header"]]["children"].append(digest)  # updating children of the parent node
            ## UPDATE BALANCE MAP ##
            prev_balance_state = self.blockchain_graph[block.get_header()["prev_header"]]["balance_map"] # get previous balance map
            prev_balance_state[block.miner_id] = prev_balance_state.get(block.miner_id, 0) + 100 # change to coins per block
            for txn in block.merkle_tree.past_transations: # updating balance from transaction
                prev_balance_state[txn["sender"]] = prev_balance_state.get(txn["sender"], 0) - txn["amount"]  
                prev_balance_state[txn["receiver"]] = prev_balance_state.get(txn["receiver"], 0) + txn["amount"]
            new_balance_map = prev_balance_state
            for bal in new_balance_map.values():
                if bal < 0:
                    return "Insufficient balance"
            ## UPDATE DIFFICULTY ##
            if block.get_header()["timestamp"] - self.blockchain_graph[block.get_header()["prev_header"]]["timestamp"] > 5:
                self.difficulty -= 1
            elif block.get_header()["timestamp"] - self.blockchain_graph[block.get_header()["prev_header"]]["timestamp"] < 5:
                self.difficulty += 1
            ## UPDATE BLOCKCHAIN ##
            self.blockchain_graph[digest] = {"children": [], "level_n": prev_level + 1, "body": block, "balance_map": new_balance_map}  # creating new node
            self.resolve()

    def create_chain_to_parent_block(self, block):
        block_list = []
        while True:
            parent_node = self.blockchain_graph[block.get_header()["prev_header"]]
            if parent_node["height"] == 0:
                break
            block_list.append(parent_node["block"])
        return block_list

    # def create_longest_chain(self, longest_header):
    #     longest_chain = []
    #     while True:
    #         parent = self.blockchain_graph[longest_header]["block"].get_header()[
    #             "prev_header"]
    #         pass

    def update_longest_header(self):
        pass

    def resolve(self):



    def _resolve(self):
        """
        get longest header and compute the longest chain through recurrence
        update balance map
        return longest chain through recurrence
        """
        highest_level_n = 0
        highest_level_n_digest = []
        for digest, node in self.graph.items():  # finding the highest level_n
            if len(node["children"]) > 1:
                print('Fork is found...')
            # check transaction
            if node["height"] > highest_level_n:
                highest_level_n_digest = []  # getting nodes with highest level_n
                highest_level_n_digest.append(digest)
                highest_level_n += 1
            elif node["height"] == highest_level_n:
                highest_level_n_digest.append(digest)
            else:
                continue
        self.longest_header = highest_level_n_digest[random.randint(
            0, len(highest_level_n_digest) - 1)]  # return a random header
        print("The longest header is now ", self.longest_header)


if __name__ == "__main__":
    bc = Blockchain()
    print(bc.blockchain_graph)
    print(bc.longest_header)

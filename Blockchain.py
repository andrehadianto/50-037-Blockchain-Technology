from Block import Block
import time
import hashlib
import cbor
import random


class Blockchain:
    # TARGET = {
    #    1: b'\x05' * 2 + b'\xff' * 254,
    #    2: b'\x00' * 2 + b'\x99' * 252,
    #    3: b'\x00' * 2 + b'\x66' * 2 + b'\xff' * 250
    # }

    def __init__(self):
        self.ratio = 1
        self.TARGET = 0x000fff0000000000000000000000000000000000000000000000000000000000
        #self.new_target = (self.TARGET * self.ratio)

        self.difficulty = 1
        self.TARGET = b'\x00' + b'\x99' * self.difficulty + \
            b'\xaa' * (256 - self.difficulty-1)
        self.blockchain_graph = {}
        self.longest_chain = []
        self.longest_header = None
        self.generate_genesis_block()

    def generate_genesis_block(self):
        """
        generating the genesis block
        """
        genesis_block = Block([], "i am genesis", None)
        counter = 0
        while True:
            if counter % 10 == 0:
                print(counter)
            nonce = str(random.randint(0, 300000))
            genesis_block.set_nonce(nonce)
            to_hash = genesis_block.serialize()
            digest = hashlib.sha256(to_hash).hexdigest()
            if self.verify_pow(digest):
                break
            counter += 1
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
        if self.difficulty > 256:
            self.difficulty = 256
        if digest < self.TARGET.hex():
            return True
        return False

    def validate_block(self, block):
        """
        ensure proof of work is valid, transactions are new, timestamp
        return block isValidated
        """
        ## CHECK INCOMING BLOCK IS MINED AFTER THE PARENT BLOCK ##
        if block.get_header()["timestamp"] < self.blockchain_graph[block.get_header()["prev_header"]]["block"].get_header()["timestamp"]:
            return False
        ## CHECK FOR DUPLICATE TRANSACTIONS ##
        for trans in block.merkle_tree.past_transactions:
            # transactions from the added block's parent all the way to the genesis.
            for block_ in self.create_chain_to_parent_block(block):
                if trans in block_.merkle_tree.past_transactions:
                    return False
        return True

    def add_block(self, block):
        digest = block.hash_header()
        prev_level = self.blockchain_graph[block.get_header()[
            "prev_header"]]["height"]
        self.blockchain_graph[block.get_header()["prev_header"]]["children"].append(
            digest)  # updating children of the parent node
        ## UPDATE BALANCE MAP ##
        prev_balance_state = self.blockchain_graph[block.get_header(
        )["prev_header"]]["balance_map"]  # get previous balance map
        prev_balance_state[block.miner_id] = prev_balance_state.get(
            block.miner_id, 0) + 100  # change to coins per block
        for txn in block.merkle_tree.past_transactions:  # updating balance from transaction
            prev_balance_state[txn["sender"]] = prev_balance_state.get(
                txn["sender"], 0) - txn["amount"]
            prev_balance_state[txn["receiver"]] = prev_balance_state.get(
                txn["receiver"], 0) + txn["amount"]
        new_balance_map = prev_balance_state
        for bal in new_balance_map.values():
            if bal < 0:
                return "Insufficient balance"
        ## UPDATE DIFFICULTY ##
        if block.get_header()["timestamp"] - self.blockchain_graph[block.get_header()["prev_header"]]["block"].get_header()["timestamp"] > 5:
            print("getting easier", self.difficulty)
            self.difficulty -= 1
            self.TARGET = b'\x00' + b'\x99' * self.difficulty + \
                b'\xaa' * (256 - self.difficulty-1)
            print(self.TARGET[0:50])
        elif block.get_header()["timestamp"] - self.blockchain_graph[block.get_header()["prev_header"]]["block"].get_header()["timestamp"] < 2:
            print("getting harder", self.difficulty)
            self.difficulty += 1
            self.TARGET = b'\x00' + b'\x99' * self.difficulty + \
                b'\xaa' * (256 - self.difficulty-1)
            print(self.TARGET[0:50])
        ## UPDATE BLOCKCHAIN ##
        self.blockchain_graph[digest] = {"children": [], "height": prev_level +
                                         1, "block": block, "balance_map": new_balance_map}  # creating new node
        self.resolve2()

    def create_chain_to_parent_block(self, block):
        block_list = []
        while True:
            parent_node = self.blockchain_graph[block.get_header()[
                "prev_header"]]
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
        pass

    def resolve2(self):
        """
        get longest header and compute the longest chain through recurrence
        update balance map
        return longest chain through recurrence
        """
        highest_level_n = 0
        highest_level_n_digest = []
        for digest, node in self.blockchain_graph.items():  # finding the highest level_n
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

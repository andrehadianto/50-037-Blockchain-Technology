from Block import Block
import time
import hashlib
import cbor
import random
import copy


class Blockchain:
    MIN_TARGET = 9.0147377111333645e+70

    def __init__(self):
        self.TARGET = 2.188913362042147e+71
        self.blockchain_graph = {}
        self.longest_chain = []
        self.longest_header = None
        self.generateGenesisBlock()
        self.old_target = self.TARGET

    def generateGenesisBlock(self):
        """
        generating the genesis block
        """
        genesis_block = Block([], "i am genesis", None, "0", 0)
        digest = genesis_block.hash_header()
        self.blockchain_graph[digest] = {
            "children": [],
            "height": 0,
            "block": genesis_block,
            "balance_map": {'pawel'.encode('utf-8').hex(): 10000}
        }
        self.longest_header = digest

    def verifyPow(self, digest, block_target=0):
        if block_target == 0:
            block_target = self.TARGET
        if int('0x'+digest, 0) <= block_target:
            return True
        return False

    def validateBlock(self, block):
        """
        ensure proof of work is valid, transactions are new, timestamp
        return block isValidated
        """
        # ## CHECK INCOMING BLOCK IS MINED AFTER THE PARENT BLOCK ##
        # if block.get_header()["timestamp"] <= self.blockchain_graph[block.get_header()["prev_header"]]["block"].get_header()["timestamp"]:
        #     print('timeerror')
        #     return False
        ## CHECK FOR DUPLICATE CHILDREN ##
        if block.hash_header() in self.blockchain_graph:
            return False
        ## CHECK FOR DUPLICATE TRANSACTIONS ##
        for trans in block.merkle_tree.past_transactions:
            for block_ in self.createChainToParentBlock(block):
                for trans_ in block_.merkle_tree.past_transactions:
                    if trans.serialize() == trans_.serialize():
                        print('repeated transactions')
                        return False
                
        
        return True

    def getNodeBalanceMap(self, digest):
        return self.blockchain_graph[digest]["balance_map"]

    def addBlock(self, block):
        digest = block.hash_header()
        prev_level = self.blockchain_graph[block.get_header()[
            "prev_header"]]["height"]
        self.blockchain_graph[block.get_header()["prev_header"]]["children"].append(
            digest)  # updating children of the parent node
        ## UPDATE BALANCE MAP ##
        new_balance_map = copy.deepcopy(
            self.getNodeBalanceMap(block.get_header()["prev_header"]))
        new_balance_map[block.miner_id] = new_balance_map.get(
            block.miner_id, 0) + 100  # change to coins per block
        for txn in block.merkle_tree.past_transactions:  # updating balance from transaction
            new_balance_map[txn.sender] = new_balance_map.get(
                txn.sender, 0) - txn.amount
            new_balance_map[txn.receiver] = new_balance_map.get(
                txn.receiver, 0) + txn.amount
        for bal in new_balance_map.values():
            if bal < 0:
                return "Insufficient balance"
        ## UPDATE DIFFICULTY ##
        expected = 3.0
        time_diff = block.get_header()["timestamp"] - self.blockchain_graph[block.get_header()[
            "prev_header"]]["block"].get_header()["timestamp"]
        ratio = float(time_diff/expected)
        if ratio > 1.5:
            ratio = 1.5
        if ratio < 0.95:
            ratio = 0.95
        self.old_target = self.TARGET
        self.TARGET *= ratio
        if self.TARGET < Blockchain.MIN_TARGET:
            self.TARGET = Blockchain.MIN_TARGET
        ## UPDATE BLOCKCHAIN ##
        self.blockchain_graph[digest] = {"children": [], "height": prev_level +
                                         1, "block": block, "balance_map": new_balance_map}  # creating new node
        self.resolve2()
        

    def createChainToParentBlock(self, block):
        block_list = []
        parent_node = self.blockchain_graph[block.get_header()[
            "prev_header"]]
        parent_height = parent_node["height"]
        while parent_height > 0:
            block_list.append(parent_node["block"])
            parent_node = self.blockchain_graph[parent_node["block"].get_header()[
                "prev_header"]]
            # parent_node = self.blockchain_graph[block.get_header()[
            #     "prev_header"]]
            parent_height -= 1
        block_list.append(self.blockchain_graph["4a18a58e969d9281c65ff9fdc9443f23ce2484c532329a99c14f58b5eaef5120"]["block"])
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
            # if len(node["children"]) > 1:
            #     print('Fork is found...')
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
        print("==RESOLVE==")
        print("The longest header is now ", self.longest_header)
        print("-----------")

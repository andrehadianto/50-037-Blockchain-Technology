import hashlib
from Block import Block
import random


class Miner:
    new_block_queue = []
    trans_pool = []

    def __init__(self, miner_id, blockchain, naughty=""):
        self.miner_id = miner_id
        self.blockchain = blockchain
        self.isMining = False
        self.naughty = naughty

    def found_new_block(self, block):
        Miner.new_block_queue.append(block)

    def start_mining(self):
        ## RECEIVE NEW ANNOUNCEMENT ##
        for block in Miner.new_block_queue:
            print('new block queue')
            to_hash = block[0].serialize()
            digest = hashlib.sha256(to_hash.encode('utf-8')).hexdigest()
            print('hash of announced block', digest)
            if self.blockchain.verify_pow(digest, block[1]):
                if self.blockchain.validate_block(block[0]):
                    self.blockchain.add_block(block[0])
            print("NEW BLOCK QUEUE", self.miner_id)
            Miner.new_block_queue.remove(block)
        list_of_trans = []
        bal_map = self.blockchain.blockchain_graph[self.blockchain.longest_header]["balance_map"]
        ## COLLECT VALID TRANSACTIONS ##
        if len(Miner.trans_pool) > 0:
            for trans in Miner.trans_pool:
                if bal_map[trans.sender] - trans.amount > 0:
                    list_of_trans.append(trans)
                else:
                    print("Insufficient Balance")
                if len(list_of_trans) > 3:
                    break
        ## GENERATE NONCE ##
        new_block = Block(
            list_of_trans, self.blockchain.longest_header, self.miner_id)
        counter = 0
        while True:
            if counter % 100000 == 0:
                print("attempt:", counter)
            counter += 1
            if Miner.new_block_queue:
                return "receive new block"
            generate_nonce = str(random.randint(0, 300000))
            new_block.header['nonce'] = generate_nonce
            to_hash = new_block.serialize()
            digest = hashlib.sha256(to_hash.encode('utf-8')).hexdigest()
            ## TRY ADDING BLOCK TO MINER'S BLOCKCHAIN ##
            # try:
            if self.blockchain.verify_pow(digest):
                if self.blockchain.validate_block(new_block):
                    self.blockchain.add_block(new_block)
                    for trans in list_of_trans:
                        if trans in Miner.trans_pool:
                            Miner.trans_pool.remove(trans)
                    return new_block
            # except Exception as e:
            #     print("error: ", e)
            #     return "error"

    def evil51_mining(self, evil_header):
        ## RECEIVE NEW ANNOUNCEMENT ##
        for block in Miner.new_block_queue:
            to_hash = block.serialize()
            digest = hashlib.sha256(to_hash.encode('utf-8')).hexdigest()
            print('hash of announced block', digest)
            if self.blockchain.verify_pow(digest):
                if self.blockchain.validate_block(block):
                    self.blockchain.add_block(block)
            Miner.new_block_queue.remove(block)
        self.blockchain.longest_header = evil_header
        list_of_trans = []
        bal_map = self.blockchain.blockchain_graph[self.blockchain.longest_header]["balance_map"]
        ## COLLECT VALID TRANSACTIONS ##
        if len(Miner.trans_pool) > 0:
            for trans in Miner.trans_pool:
                print(trans.comment)
                if bal_map[trans.sender] - trans.amount > 0:
                    list_of_trans.append(trans)
                else:
                    print("Insufficient Balance")
                if len(list_of_trans) > 3:
                    break
        ## GENERATE NONCE ##
        new_block = Block(
            list_of_trans, self.blockchain.longest_header, self.miner_id)
        # counter = 0
        while True:
            # if counter % 100000 == 0:
            #     print("attempt:", counter)
            # counter += 1
            if Miner.new_block_queue:
                return "receive new block"
            generate_nonce = str(random.randint(0, 300000))
            new_block.header['nonce'] = generate_nonce
            to_hash = new_block.serialize()
            digest = hashlib.sha256(to_hash.encode('utf-8')).hexdigest()
            ## TRY ADDING BLOCK TO MINER'S BLOCKCHAIN ##
            # try:
            if self.blockchain.verify_pow(digest) and self.blockchain.validate_block(new_block):
                self.blockchain.add_block(new_block)
                for trans in list_of_trans:
                    if trans in Miner.trans_pool:
                        Miner.trans_pool.remove(trans)
                return new_block
            # except Exception as e:
            #     print("error: ", e)
            #     return "error"

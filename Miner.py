import hashlib
from Block import Block
import random

class Miner:
    new_block_queue = []

    def __init__(self, miner_id, blockchain, t_list):
        self.miner_id = miner_id
        self.blockchain = blockchain
        # self.trans_pool = []  # will be updated by MinerApp. SPVApp will broadcast to MinerApp
        self.trans_pool = t_list
        self.isMining = False

    def found_new_block(self, block):
        Miner.new_block_queue.append(block)

    def start_mining(self):
        """
        if have transaction, take transaction
        else keep mining
        """
        # while self.isMining:
        ## RECEIVE NEW ANNOUNCEMENT ##
        for block in Miner.new_block_queue:
            to_hash = block.serialize()
            digest = hashlib.sha256(to_hash.encode('utf-8')).hexdigest()
            if self.blockchain.verify_pow(digest) and self.blockchain.validate_block(block):
                self.blockchain.add_block(block)
            Miner.new_block_queue.remove(block)
        list_of_trans = []
        bal_map = self.blockchain.blockchain_graph[self.blockchain.longest_header]["balance_map"]
        ## COLLECT VALID TRANSACTIONS ##
        if len(self.trans_pool) > 0:
            for trans in self.trans_pool:
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
            counter+= 1
            if Miner.new_block_queue:
                return "receive new block"
            generate_nonce = str(random.randint(0, 300000))
            new_block.header['nonce'] = generate_nonce
            to_hash = new_block.serialize().encode('utf-8')
            digest = hashlib.sha256(to_hash).hexdigest()
            ## TRY ADDING BLOCK TO MINER'S BLOCKCHAIN ##
            # try:
            if self.blockchain.verify_pow(digest) and self.blockchain.validate_block(new_block):
                self.blockchain.add_block(new_block)
                for trans in list_of_trans:
                    if trans in self.trans_pool:
                        self.trans_pool.remove(trans)
                return new_block
            # except Exception as e:
            #     print("error: ", e)
            #     return "error"


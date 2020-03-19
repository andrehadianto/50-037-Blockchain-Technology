import hashlib

class Miner:
    new_block_queue = []

    def __init__(self, miner_id, blockchain):
        self.miner_id = miner_id
        self.blockchain = blockchain
        self.trans_pool = []  # will be updated by MinerApp. SPVApp will broadcast to MinerApp
        self.isMining = False

    def found_new_block(self,block):
        Miner.new_block_queue.append(block)

    def start_mining(self):
        """
        if have transaction, take transaction
        else keep mining
        """
        self.isMining = True
        while self.isMining:
            ## RECEIVE NEW ANNOUNCEMENT ##
            for block in Miner.new_block_queue:
                if self.blockchain.verify_pow(hashlib.sha256(block.serialize()).hexdigest()):
                    self.blockchain.add_block(block)
            list_of_trans = []
            for trans in self.trans_pool:
                # TODO: append selected trans from pool to list_of_trans
                # TODO: check if transaction in trans_pool is valid
                # TODO: check if account related to transaction has enough balance
                pass

            new_block = Block(list_of_trans, self.blockchain.longest_header, self.miner_id)
            while not Miner.new_block_queue: # noe
                # TODO: announce longest header
                pass






# new block queue update, must be an API call from MinerApp. Calling this API will update the new_block_queue in the Miner class
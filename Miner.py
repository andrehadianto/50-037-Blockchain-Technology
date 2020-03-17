class Miner:
    def __init__(self, miner_id, blockchain):
        self.miner_id = miner_id
        self.blockchain = blockchain
        self.trans_pool = [] # will be updated by MinerApp. SPVApp will broadcast to MinerApp
        self.isMining = False

    def start_mining(self):
        """
        if have transaction, take transaction
        else keep mining
        """
        self.isMining = True
        while self.isMining:
            #TODO:dododoodododo
            list_of_trans = []
            for trans in self.trans_pool:
                #TODO: append selected trans from pool to list_of_trans
                #TODO: check if transaction in trans_pool is valid
                #TODO: check if account related to transaction has enough balance
                pass

            new_block = Block(list_of_trans, self.blockchain.longest_header, self.miner_id)
            while True:
                #TODO: announce longest header
                pass


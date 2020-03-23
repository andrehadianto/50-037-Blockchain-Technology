from Transaction import Transaction
from Blockchain import Blockchain

class SPVClient:
    def __init__(self, pub_key, priv_key):
        self.pub_key = pub_key
        self.priv_key = priv_key
        self.block_headers = []
        self.balance = 0


    def receive_header(self, blockchain):
        for block in blockchain.longest_chain:
            self.block_headers.append(block.get_header())
        return self.block_headers

    def receive_transaction(self, transaction):
        pass

    def verify_transaction(self, transaction): #verify if the transaction is in the blockchain 
        pass

    def send_transaction(self, receiver, amount, comment):
        utxo = Transaction(self.pub_key, receiver, amount, comment)
        utxo.sign(priv_key)
        self.balance += amount
        return utxo
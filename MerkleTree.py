import hashlib
import math


class MerkleTree():

    def __init__(self):
        self.past_transactions = []
        self.past_hashes = []
        self.tiered_node_list = []
        self.root = None

    def add(self, transaction):
        digest = hashlib.sha256(transaction.serialize().encode('utf-8')).hexdigest()
        self.past_transactions.append(transaction)
        self.past_hashes.append(digest)
        return digest

    def build(self):
        if len(self.past_transactions) > 0:
            merkle_chain = []
            merkle_chain.append(self.past_hashes)
            while (math.log2(len(merkle_chain[0])).is_integer()) == False:
                merkle_chain[0].append(None)

            n = len(merkle_chain[0])
            n_level = math.ceil(math.log2(n))
            cycle = 0
            while n != 1:

                level_ = []
                for i in range(0, n, 2):
                    if merkle_chain[cycle][i+1] == None:
                        to_hash = str(merkle_chain[cycle][i])
                        digest = hashlib.sha256(to_hash.encode()).hexdigest()
                        level_.append(digest)
                    if merkle_chain[cycle][i] == None:
                        level_.append(None)
                    else:
                        to_hash = str(merkle_chain[cycle][i]) + \
                            str(merkle_chain[cycle][i+1])
                        digest = hashlib.sha256(to_hash.encode()).hexdigest()
                        level_.append(digest)
                cycle += 1
                merkle_chain.append(level_)
                n = math.ceil(n/2)
            self.merkle_chain = merkle_chain
        else:
            self.merkle_chain = []

    def get_root(self):
        return self.merkle_chain[-1] if self.merkle_chain else None

    def get_leaves(self):
        return self.merkle_chain[0] if self.merkle_chain else None

    def get_min_nodes(self, transaction):
        idx = self.past_transactions.index(transaction)
        original_idx = idx
        if len(self.merkle_chain)== 1:
            return [],None,original_idx
        # get bottom up
        nodes = []
        if idx % 2 == 0:
            # means left node
            state = "left"
            neighbour = self.merkle_chain[0][idx+1]
        else:
            neighbour = self.merkle_chain[0][idx-1]
            state = "right"
        level = 1
        idx = idx//2
        while level != len(self.merkle_chain) - 1:
            if idx % 2 == 0:
                # My node is on the left, the one being appended is on the right
                state = "Right"
                nop = self.merkle_chain[level][idx+1]
            else:
                # my node is on the right, the one being appended is on the left
                nop = self.merkle_chain[level][idx-1]
                state = "Left"
            nodes.append([nop, state])
            level += 1
            idx = idx//2
        return nodes, neighbour, original_idx

    def get_proof(self, transaction, root):
        nodes, neighbour, idx = self.get_min_nodes(transaction)
        digest = hashlib.sha256(transaction).hexdigest()

        if idx % 2 == 0:
            # the node is on the left
            to_hash = str(digest) + str(neighbour)
            digest = hashlib.sha256(to_hash.encode()).hexdigest()
        else:
            # node is on the right
            to_hash = str(neighbour) + str(digest)
            digest = hashlib.sha256(to_hash.encode()).hexdigest()
        for i in nodes:
            if i[1] == "Left":
                # my node is right, my neighbour is left. Left goes first
                to_hash = str(i[0]) + str(digest)
                digest = hashlib.sha256(to_hash.encode()).hexdigest()
            else:
                to_hash = str(digest) + str(i[0])
                digest = hashlib.sha256(to_hash.encode()).hexdigest()
        if digest == root[0]:
            return "True"
        else:
            return "False"

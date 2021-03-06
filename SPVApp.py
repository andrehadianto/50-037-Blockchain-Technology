from flask import Flask, request
import requests
from Transaction import Transaction
#from SPVClient import SPVClient
from KeyGen import generateKeyPair
import argparse
import json
import ecdsa
import hashlib

app = Flask(__name__)

MINERS_PORT_LIST = [5004, 5005]

list_of_headers = []
longest_miner = 0
txn_and_proofs = {}


@app.route('/broadcast_transactions', methods=["POST"])
def broadcast_transactions():
    res = json.loads(request.get_json())
    pub_key = res["pub_key"]
    priv_key = res["priv_key"]
    receiver = res["receiver"]
    amount = res["amount"]
    comment = res["comment"]

    print("Receiving broadcast request from {}".format(pub_key[0:6]))
    trans = createTransaction(pub_key, receiver, amount, comment, priv_key)
    trans = trans.serialize()
    print('SERIALIZED TRANSACTION', trans)
    for port in MINERS_PORT_LIST:
        r = requests.post(
            "http://localhost:{}/new_transactions".format(port), json=trans)
        print("Broadcast {}".format(port))
    return "200" if r.ok else "500"


def createTransaction(sender, receiver, amount, comment, priv_key):
    transaction = Transaction(sender, receiver, amount, comment)
    print('createTransaction:', priv_key)
    transaction.sign(ecdsa.SigningKey.from_string(bytes.fromhex(priv_key)))
    return transaction

@app.route('/headers',methods = ["POST"])
def getHeaders():
    global list_of_headers
    global longest_miner
    # wait for miners to send the longest chain
    res = json.loads(request.get_json())
    chain_length = len(res['list_headers'])
    if chain_length > len(list_of_headers):
        list_of_headers = res['list_headers']
        longest_miner = res['miner_port']
    
    return "200"


@app.route('/list_transactions', methods=['POST'])
def get_related_transactions():
    # send request to miners
    # this is the longest guy
    data = request.get_json()
    r = requests.post(
        "http://localhost:{}/get_transactions".format(5005), json=data)
    res = r.json()
    print("THE TRANSACTION LIST FROM MINER:", res)
    transaction_list = []
    pub_key = data['pub']
    # After u get the txn params here, have to initialize a new txn
    for trans_ in res['transaction_list']:
        trans = json.loads(trans_[0])
        sender = trans["sender"]
        receiver = trans["receiver"]
        amount = trans["amount"]
        comment = trans["comment"]
        timestamp = trans["timestamp"]
        signature = trans["signature"]
        t = Transaction(sender, receiver, amount,
                        comment, timestamp, signature)
        transaction_list.append(t)

        txn_and_proofs[pub_key] = txn_and_proofs.get(pub_key, [])

        txn_and_proofs[pub_key].append( {"transaction" : t, "nodes" : trans_[1], "neighbour":trans_[2], "index" : trans_[3] } )

    # this should get test
    print(transaction_list)
    return 'success', 200


@app.route('/verify', methods=['POST'])
def verify_transactions():
    trans = request.get_json()
    sender = trans["sender"]
    receiver = trans["receiver"]
    amount = trans["amount"]
    comment = trans["comment"]
    timestamp = trans["timestamp"]
    signature = trans["signature"]
    t = Transaction(sender, receiver, amount,
                        comment, timestamp, signature)
        
    for pub_key_trans in txn_and_proofs.values():
        for trans in pub_key_trans:
            if t == trans["transaction"]:
                print('found matching transaction')
                #VERIFY IT
                to_hash = trans["transaction"].serialize()
                digest = hashlib.sha256(to_hash.encode()).hexdigest()
                if trans['nodes'] == [] and trans['neighbour'] == None:
                    #check if digest in longest chain
                    for header in list_of_headers:
                        if header["root"] is None:
                            continue
                        print(header["root"])
                        if digest == header['root'][0]:
                            print("Transaction Verified")
                            return "success",200
                else:
                    if trans["index"] % 2 == 0:
                        # the node is on the left
                        to_hash = str(digest) + str(trans["neighbour"])
                        digest = hashlib.sha256(to_hash.encode()).hexdigest()
                    else:
                        # node is on the right
                        to_hash = str(trans['neighbour']) + str(digest)
                        digest = hashlib.sha256(to_hash.encode()).hexdigest()
                    if trans["nodes"][1] == 'left':
                        to_hash = str(trans["nodes"][0]) + str(digest)
                        digest = hashlib.sha256(to_hash.encode()).hexdigest()
                    else:
                        to_hash = + str(digest)+ str(trans["nodes"][0]) 
                        digest = hashlib.sha256(to_hash.encode()).hexdigest()
                    for header in list_of_headers:
                        if header["timestamp"] < timestamp:
                            continue
                        if digest == header['root'][0]:
                            print("Transaction verified")
                            return "success",200
    return "error",500
                    



    

    # for txns in txn_and_proofs[sender].values():
    #     if txn == txn[0]:
    #         # hash the rest and perform check
    #         timestamp = txn['timestamp']
    #         for header in list_of_headers:
    #             if timestamp > i["timestamp"]:
    #                 continue
    #             else:
    #                 nodes, neighbour, idx = txn[1], txn[2], txn[3]
    #                 # call a miner and ask him to return me the outputs of block.merkle_tree.get_min_nodes()
    #                 # reconstruct tree
    #                 digest = hashlib.sha256(txn).hexdigest()
    #                 if idx % 2 == 0:
    #                     # the node is on the left
    #                     to_hash = str(digest) + str(neighbour)
    #                     digest = hashlib.sha256(to_hash.encode()).hexdigest()
    #                 else:
    #                     # node is on the right
    #                     to_hash = str(neighbour) + str(digest)
    #                     digest = hashlib.sha256(to_hash.encode()).hexdigest()
    #                 for i in nodes:
    #                     if i[1] == "Left":
    #                         # my node is right, my neighbour is left. Left goes first
    #                         to_hash = str(i[0]) + str(digest)
    #                         digest = hashlib.sha256(
    #                             to_hash.encode()).hexdigest()
    #                     else:
    #                         to_hash = str(digest) + str(i[0])
    #                         digest = hashlib.sha256(
    #                             to_hash.encode()).hexdigest()
    #                 if digest == i["root"]:
    #                     return True


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

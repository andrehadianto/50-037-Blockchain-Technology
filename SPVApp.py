from flask import Flask, request
import requests
from Transaction import Transaction
#from SPVClient import SPVClient
from KeyGen import generateKeyPair
import argparse
import json
import ecdsa

app = Flask(__name__)

MINERS_PORT_LIST = [5004,5005]

list_of_headers = []
longest_miner = 0

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
        r = requests.post("http://localhost:{}/new_transactions".format(port), json=trans)
        print("Broadcast {}".format(port))
    return "200" if r.ok else "500"

def createTransaction(sender, receiver, amount, comment, priv_key):
    transaction = Transaction(sender, receiver, amount, comment)
    print('createTransaction:', priv_key)
    transaction.sign(ecdsa.SigningKey.from_string(bytes.fromhex(priv_key)))
    return transaction

@app.route('/headers',methods = ["POST"])
def get_headers():
    global list_of_headers
    global longest_miner
    #wait for miners to send the longest chain
    res = json.loads(request.get_json())
    chain_length = len(res['list_headers'])
    if chain_length > len(list_of_headers):
            list_of_headers = res['list_headers']
            longest_miner = res['miner_port']
    # print(chain_length)
    # print(list_of_headers)
    return "200"


@app.route('/list_transactions',methods=['POST'])
def get_related_transactions():
    #send request to miners
    #this is the longest guy
    data = request.get_json()
    print(longest_miner)
    r = requests.post("http://localhost:{}/get_transactions".format(longest_miner),json=data)
    res = r.json()
    print("THE TRANSACTION LIST FROM MINER:" , res)
    transaction_list = []
    # After u get the txn params here, have to initialize a new txn
    for trans in res['transaction_list']:
        trans = json.loads(trans)
        print("SERIALIZED TRANSACTION FROM GET: ",transaction_list)
        sender = trans["sender"]
        receiver = trans["receiver"]
        amount = trans["amount"]
        comment = trans["comment"]
        timestamp = trans["timestamp"]
        signature = trans["signature"]
        t = Transaction(sender, receiver, amount, comment, timestamp, signature)
        transaction_list.append(t)

    # this should get test

    return 'success',200
     
def verify_transactions(txn):
    timestamp = txn.timestamp
    for header in list_of_headers:
        if timestamp > i["timestamp"] :
            continue
        else:
            nodes,neighbour,idx = call_miner(header,txn)
            # call a miner and ask him to return me the outputs of block.merkle_tree.get_min_nodes()
            #reconstruct tree
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
            if digest == i["root"]:
                return True

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

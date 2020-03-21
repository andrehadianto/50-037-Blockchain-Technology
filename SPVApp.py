from flask import Flask, request
import requests
from Transaction import Transaction
from SPVClient import SPVClient
from KeyGen import generateKeyPair
import argparse
import json
import ecdsa

app = Flask(__name__)

MINERS_PORT_LIST = [5005]

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

#def get_headers():
    #for each miner get longest chain
    # 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

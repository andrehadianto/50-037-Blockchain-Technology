from flask import Flask, request, redirect
import requests
import json
import os
import time
import argparse
from Block import Block
from Blockchain import Blockchain
from Miner import Miner
from Transaction import Transaction
from KeyGen import generateKeyPair
import cbor
import hashlib

app = Flask(__name__)

FOUNDER = 'pawel'.encode('utf-8').hex()
PORT_LIST = [5005, 7337, 7338]
PORT_LIST_51 = [7337, 7338]
CLIENT_PORT = 8080

stopEvil = False

priv_key, pub_key = generateKeyPair()
priv_key = priv_key.to_string().hex()
pub_key = pub_key.to_string().hex()

sutdcoin = Blockchain()
print('Genesis block generated')
print(sutdcoin.blockchain_graph)

@app.route('/show_graph')
def show_graph():
    print("==============BLOCKCHAIN===========")
    for k, v in sutdcoin.blockchain_graph.items():
        print("-----")
        print(k)
        print("owner:", v["block"].miner_id)
        print("height:", v['height'])
        # print("block:", v['block'].get_header())
        # print("balance map:", v['balance_map'])
        print("children:", v['children'])
    print("==================================")
    return "200"

@app.route('/create_transaction1', methods=["POST"])
def prepare_transaction_to_send():
    res = request.get_json()
    amount = res["amount"]
    comment = res["comment"]
    receiver = res["receiver"]

    data = {}
    data["pub_key"] = pub_key
    data["priv_key"] = priv_key
    data["receiver"] = receiver.encode('utf-8').hex()
    data["amount"] = amount
    data["comment"] = comment
    data = json.dumps(data)
    r = requests.post("http://localhost:{}/broadcast_transactions".format(CLIENT_PORT), json=data)
    return "200" if r.ok else "500"

@app.route('/new_transactions', methods=["POST"])
def update_transaction_pool():
    res = json.loads(request.get_json())

    sender = res["sender"]
    receiver = res["receiver"]
    amount = res["amount"]
    comment = res["comment"]
    timestamp = res["timestamp"]
    signature = res["signature"]

    trans = Transaction(sender, receiver, amount, comment, timestamp, signature)
    if trans.validate_signature():
        myMiner.trans_pool.append(trans)
    else:
        return "500"
    return "200"

@app.route('/listen', methods=["POST"])
def listen_to_broadcast():
    res = json.loads(request.get_json())
    if res.get("stop"):
        stopEvil = True
        return 'success',200


    difficulty = res["difficulty"]
    evil = res["evil"]
    transaction_list = []
    for trans in res["transactions"]:
        transaction_list.append(Transaction.deserialize(trans))
    block = Block(transaction_list, res['header']
                  ['prev_header'], res['miner_id'], res['header']['nonce'], res['header']['timestamp'])
    myMiner.new_block_queue.append([block,difficulty,evil])
    return 'success', 200
    # except Exception as e:
    #     return {"Exception": str(e)}, 500
#     params = request.get_json()

def announce(block, isEvil=False):
    PORTS = PORT_LIST_51 if isEvil else PORT_LIST
    for port in PORTS:
        if port == args.port:
            continue
        print("I am announcing to: {}".format(port))
        print(block.serialize())
        try:
            data = {}
            data['header'] = block.get_header()
            data['difficulty'] = sutdcoin.old_target
            data["evil"] = "evil" if isEvil else "good"
            transactions_to_send = []
            for trans in block.merkle_tree.past_transactions:
                transactions_to_send.append(trans.serialize())
            data['transactions'] = transactions_to_send
            data['miner_id'] = myMiner.miner_id
            form = json.dumps(data)
            r = requests.post(
                "http://localhost:{}/listen".format(port), json=form)
        except Exception as e:
            return {"Exception": str(e)}, 500
    latest_block = sutdcoin.blockchain_graph[sutdcoin.longest_header]["block"]
    latest_chain = sutdcoin.create_chain_to_parent_block(latest_block)
    chain_of_headers = []
    for i in latest_chain:
        head = i.get_header()
        chain_of_headers.append(head)
    d1 = {}
    d1['list_headers'] = chain_of_headers
    d1 = json.dumps(d1)
    r = requests.post("http://localhost:{}/headers".format(8080),json=d1)
        
    if r.ok:
        return 'success', 200
    else:
        return 'not ok', 400

def announce_51(stop):
    for port in PORT_LIST_51:
        if port == args.port:
            continue
        print("I am announcing to: {}".format(port))
        print(block.serialize())
        if stop == "stop":
            form = {}
            form['stop'] = 'stop'
            form = json.dumps(form)
            r = requests.post("http://localhost:{}/listen".format(port), json=form)
    if r.ok:
        return 'success', 200
    else:
        return 'not ok', 400

@app.route('/start_mining')
def start_mining():
    myMiner.isMining = True
    time.sleep(2)
    while True:
        # try:
        res = myMiner.start_mining()
        if res == "receive new block":
            continue
        elif res == "error":
            continue
        # except Exception as e:
        #     return {"Exception": str(e)}, 500
        announce(res)

        # print("==============BLOCKCHAIN===========")
        # for k, v in sutdcoin.blockchain_graph.items():
        #     print("-----")
        #     print(k)
        #     print("owner:", v["block"].miner_id)
        #     print("height:", v['height'])
        #     # print("block:", v['block'].get_header())
        #     print("balance map:", v['balance_map'])
        #     print("children:", v['children'])
        # print("==================================")
@app.route('/start_mining_51')
def start_mining_51():
    myMiner.isMining = True
    time.sleep(2)
    counter = 0
    
    while counter <= 4:
        counter += 1
        # try:
        res = myMiner.start_mining()
        if res == "receive new block":
            continue
        elif res == "error":
            continue
        # except Exception as e:
        #     return {"Exception": str(e)}, 500
        announce(res)

    print("COMMENCING EVIL DEEDS")
    good_length = 4
    evil_length = 0
    evil_head = sutdcoin.blockchain_graph["4a18a58e969d9281c65ff9fdc9443f23ce2484c532329a99c14f58b5eaef5120"]["children"][0]
    while evil_length < good_length:
        if stopEvil:
            break
        res = myMiner.evil51_mining(evil_head)
        if res == "receive new block":
            good_length += 1
            continue
        if res == "receive evil block":
            evil_length += 1
            continue
        elif res == "error":
            continue
        # except Exception as e:
        #     return {"Exception": str(e)}, 500
        evil_head = hashlib.sha256(res.serialize().encode('utf-8')).hexdigest()
        evil_length = len(sutdcoin.create_chain_to_parent_block(res)) + 1
        if evil_length > good_length:
            announce_51("stop")
        announce(res, isEvil=True)

        # print("==========EVILBLOCKCHAIN===========")
        # for k, v in sutdcoin.blockchain_graph.items():
        #     print("-----")
        #     print(k)
        #     print("owner:", v["block"].miner_id)
        #     print("height:", v['height'])
        #     # print("block:", v['block'].get_header())
        #     print("balance map:", v['balance_map'])
        #     print("children:", v['children'])
        # print("==================================")
    evil_block_list = sutdcoin.create_chain_to_parent_block(res)
    evil_block_list.insert(0, res)
    if not stopEvil:
        for block in reversed(evil_block_list):
            announce(block)
    print("EVIL DEED IS DONE")
    while True:
        res = myMiner.start_mining()
        if res == "receive new block":
            continue
        elif res == "error":
            continue
        # except Exception as e:
        #     return {"Exception": str(e)}, 500
        announce(res)

@app.route('/update')
def update():
    update_from_blockchain = True



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Configure miners")
    parser.add_argument('-p', '--port', type=int, required=True, help="PORT")
    parser.add_argument('-e', '--evil', type=bool, required=False, help="51% Attack")
    args = parser.parse_args()

    myMiner = Miner(pub_key, sutdcoin)
    PORT = args.port
    app.run(host="0.0.0.0", port=PORT, debug=True)

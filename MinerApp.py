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
PORT_LIST = [5004, 5005]
PORT_LIST_51 = [7337, 7338]
CLIENT_PORT = 8080


priv_key, pub_key = generateKeyPair()
priv_key = priv_key.to_string().hex()
pub_key = pub_key.to_string().hex()
print(pub_key)

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
        print("balance map:", v['balance_map'])
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
    r = requests.post(
        "http://localhost:{}/broadcast_transactions".format(CLIENT_PORT), json=data)
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

    trans = Transaction(sender, receiver, amount,
                        comment, timestamp, signature)
    if trans.validate_signature():
        myMiner.trans_pool.append(trans)
    else:
        return "500"
    return "200"


@app.route('/listen', methods=["POST"])
def listen_to_broadcast():
    res = json.loads(request.get_json())
    difficulty = res["difficulty"]
    transaction_list = []
    for trans in res["transactions"]:
        transaction_list.append(Transaction.deserialize(trans))
    block = Block(transaction_list, res['header']
                  ['prev_header'], res['miner_id'], res['header']['nonce'], res['header']['timestamp'])
    myMiner.new_block_queue.append([block, difficulty])
    return 'success', 200
    # except Exception as e:
    #     return {"Exception": str(e)}, 500
#     params = request.get_json()


def announce(block):
    for port in PORT_LIST:
        if port == args.port:
            continue
        print("I am announcing to: {}".format(port))
        try:
            data = {}
            data['header'] = block.get_header()
            data['difficulty'] = sutdcoin.old_target
            transactions_to_send = []
            for trans in block.merkle_tree.past_transactions:
                transactions_to_send.append(trans.serialize())
            data['transactions'] = transactions_to_send
            # to get the longest one, used by /headers endpoint
            data['miner_id'] = myMiner.miner_id

            form = json.dumps(data)
            r = requests.post(
                "http://localhost:{}/listen".format(port), json=form)
            print('done sending')
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
    d1['miner_port'] = PORT
    print(d1)
    d1 = json.dumps(d1)

    r = requests.post("http://localhost:{}/headers".format(8080), json=d1)

    if r.ok:
        return 'success', 200
    else:
        return 'not ok', 400


def announce_51(block):
    for port in PORT_LIST_51:
        if port == args.port:
            continue
        print("I am announcing to: {}".format(port))
        try:
            data = {}
            data['header'] = block.get_header()
            transactions_to_send = []
            for trans in block.merkle_tree.past_transactions:
                transactions_to_send.append(trans.serialize())
            data['transactions'] = transactions_to_send
            data['miner_id'] = myMiner.miner_id

            form = json.dumps(data)
            r = requests.post(
                "http://localhost:{}/listen".format(port), json=form)
            print('done sending')
        except Exception as e:
            return {"Exception": str(e)}, 500
    if r.ok:
        return 'success', 200
    else:
        return 'not ok', 400


@app.route('/start_mining')
def start_mining():
    myMiner.isMining = True
    while True:
        time.sleep(0.5)
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

    sutdcoin.longest_header = "4a18a58e969d9281c65ff9fdc9443f23ce2484c532329a99c14f58b5eaef5120"
    good_length = 4
    evil_length = 0
    evil_head = "4a18a58e969d9281c65ff9fdc9443f23ce2484c532329a99c14f58b5eaef5120"
    while evil_length < good_length:
        # try:
        res = myMiner.evil51_mining(evil_head)
        if res == "receive new block":
            good_length += 1
            continue
        elif res == "error":
            continue
        # except Exception as e:
        #     return {"Exception": str(e)}, 500
        announce_51(res)
        evil_head = hashlib.sha256(res.serialize().encode('utf-8')).hexdigest()
        evil_length = len(sutdcoin.create_chain_to_parent_block(res)) + 1

        print("==========EVILBLOCKCHAIN===========")
        for k, v in sutdcoin.blockchain_graph.items():
            print("-----")
            print(k)
            print("height:", v['height'])
            # print("block:", v['block'].get_header())
            print("balance map:", v['balance_map'])
            print("children:", v['children'])
        print("==================================")
    evil_block_list = sutdcoin.create_chain_to_parent_block(res)
    evil_block_list.insert(0, res)
    for block in reversed(evil_block_list):
        announce(block)
    print("EVIL DEED IS DONE")


@app.route('/update')
def update():
    update_from_blockchain = True


# @app.route('/my_transactions'):
# def verify_my_transaction:
#     r = requests.get("http://localhost:{}/list_transactions/{}".format(CLIENT_PORT,pub_key))
#     if r.ok:
#         return 200
#     else:
#         return 400

@app.route('/get_transactions', methods=['POST'])
def listening_to_my_transactions():
    user_pub_key = request.get_json()['pub']
    print(user_pub_key)
    # need to serialize transaction and then make on other side
    transactions_list = []
    data = {}
    # print(sutdcoin.blockchain_graph)
    blockchain_graph_items = sutdcoin.blockchain_graph.items()
    for k, v in blockchain_graph_items:
        for trans in v['block'].merkle_tree.past_transactions:
            if trans.sender == user_pub_key or trans.receiver == user_pub_key:
                nodes, neighbour, index = v['block'].merkle_tree.get_min_nodes(
                    trans)
                transactions_list.append(
                    [trans.serialize(), nodes, neighbour, index])

    #     print("-----")
    #     print(k) #header
    #     print("height:", v['height'])
    #     # print("block:", v['block'].get_header())
    #     print("balance map:", v['balance_map'])
    #     print("children:", v['children'])
    # print("==================================")
    data['transaction_list'] = transactions_list
    print("THE TRANSACTION LIST IS:", data)
    data = json.dumps(data)
    return data, 200


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Configure miners")
    parser.add_argument('-p', '--port', type=int, required=True, help="PORT")
    parser.add_argument('-e', '--evil', type=bool,
                        required=False, help="51% Attack")
    args = parser.parse_args()

    myMiner = Miner(pub_key, sutdcoin)
    PORT = args.port
    app.run(host="0.0.0.0", port=PORT, debug=True)
